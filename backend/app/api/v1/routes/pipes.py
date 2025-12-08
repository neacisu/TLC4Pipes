"""
Pipes API Routes
CRUD operations for pipe catalog
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from app.api.schemas.pipe import PipeResponse, PipeCreate
from app.models.pipe_catalog import PipeCatalog
from app.core.calculators.gap_clearance import find_compatible_pipes

router = APIRouter()


@router.get("/", response_model=List[PipeResponse])
async def list_pipes(
    dn_mm: Optional[int] = Query(None, description="Filter by nominal diameter"),
    pn_class: Optional[str] = Query(None, description="Filter by pressure class"),
    sdr: Optional[int] = Query(None, description="Filter by SDR"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    List all pipes from the catalog with optional filters.
    """
    query = select(PipeCatalog)
    
    if dn_mm is not None:
        query = query.where(PipeCatalog.dn_mm == dn_mm)
    if pn_class is not None:
        query = query.where(PipeCatalog.pn_class == pn_class)
    if sdr is not None:
        query = query.where(PipeCatalog.sdr == sdr)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    pipes = result.scalars().all()
    
    return [
        PipeResponse(
            id=p.id,
            code=p.code,
            sdr=p.sdr,
            pn_class=p.pn_class,
            dn_mm=p.dn_mm,
            wall_mm=float(p.wall_mm),
            inner_diameter_mm=float(p.inner_diameter_mm),
            weight_per_meter=float(p.weight_per_meter)
        )
        for p in pipes
    ]


@router.get("/{pipe_id}", response_model=PipeResponse)
async def get_pipe(pipe_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific pipe by ID.
    """
    query = select(PipeCatalog).where(PipeCatalog.id == pipe_id)
    result = await db.execute(query)
    pipe = result.scalar_one_or_none()
    
    if not pipe:
        raise HTTPException(status_code=404, detail="Pipe not found")
    
    return PipeResponse(
        id=pipe.id,
        code=pipe.code,
        sdr=pipe.sdr,
        pn_class=pipe.pn_class,
        dn_mm=pipe.dn_mm,
        wall_mm=float(pipe.wall_mm),
        inner_diameter_mm=float(pipe.inner_diameter_mm),
        weight_per_meter=float(pipe.weight_per_meter)
    )


@router.get("/compatible/{pipe_id}")
async def get_compatible_pipes(
    pipe_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get pipes that can be nested (telescoped) inside the given pipe.
    Uses gap clearance formula from specification.
    """
    # Get the host pipe
    host_query = select(PipeCatalog).where(PipeCatalog.id == pipe_id)
    result = await db.execute(host_query)
    host_pipe = result.scalar_one_or_none()
    
    if not host_pipe:
        raise HTTPException(status_code=404, detail="Pipe not found")
    
    # Get all potentially compatible pipes (smaller diameter)
    candidates_query = select(PipeCatalog).where(
        PipeCatalog.dn_mm < host_pipe.dn_mm
    )
    result = await db.execute(candidates_query)
    candidates = result.scalars().all()
    
    # Convert to dicts for gap clearance calculation
    host_dict = {
        "inner_diameter_mm": float(host_pipe.inner_diameter_mm),
        "outer_diameter_mm": host_pipe.dn_mm
    }
    
    candidate_dicts = [
        {
            "id": p.id,
            "code": p.code,
            "dn_mm": p.dn_mm,
            "outer_diameter_mm": p.dn_mm,
            "sdr": p.sdr,
            "pn_class": p.pn_class,
            "weight_per_meter": float(p.weight_per_meter)
        }
        for p in candidates
    ]
    
    # Find compatible pipes using gap clearance algorithm
    compatible = find_compatible_pipes(host_dict, candidate_dicts)
    
    return {
        "outer_pipe": {
            "id": host_pipe.id,
            "code": host_pipe.code,
            "dn_mm": host_pipe.dn_mm,
            "inner_diameter_mm": float(host_pipe.inner_diameter_mm)
        },
        "compatible_inner_pipes": [
            {
                "id": p["id"],
                "code": p["code"],
                "dn_mm": p["dn_mm"],
                "available_gap_mm": round(p["clearance_result"].available_gap_mm, 1),
                "required_gap_mm": round(p["clearance_result"].required_gap_mm, 1)
            }
            for p in compatible
        ],
        "total_compatible": len(compatible)
    }
