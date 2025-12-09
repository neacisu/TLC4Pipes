"""
Calculations API Routes
Core loading optimization endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from app.models.pipe_catalog import PipeCatalog
from app.models.truck_config import TruckConfig
from app.core.calculators.gap_clearance import validate_nesting_compatibility
from app.services.loading_service import (
    calculate_loading_plan,
    loading_plan_to_dict
)


logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response schemas
class OrderItemRequest(BaseModel):
    pipe_id: int
    quantity: int = Field(..., ge=1)


class OptimizeRequest(BaseModel):
    items: List[OrderItemRequest]
    pipe_length_m: float = Field(12.0, ge=6, le=18)
    truck_config_id: Optional[int] = None
    enable_nesting: bool = True
    max_nesting_levels: int = Field(4, ge=1, le=10)


class OptimizeResponse(BaseModel):
    summary: dict
    trucks: List[dict]
    nesting_stats: dict
    weight_limits: dict
    warnings: List[str]


class NestingValidationResponse(BaseModel):
    is_valid: bool
    outer_pipe: dict
    inner_pipe: dict
    gap_available_mm: float
    gap_required_mm: float
    message: str


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_loading(
    request: OptimizeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate optimal loading plan for pipes.
    
    Uses the Matryoshka algorithm:
    1. Bundle phase: Create nested pipe bundles (telescoping)
    2. Packing phase: Pack bundles into trucks using FFD algorithm
    """
    # Load pipe data for each item
    pipe_ids = [item.pipe_id for item in request.items]
    pipes_query = select(PipeCatalog).where(PipeCatalog.id.in_(pipe_ids))
    result = await db.execute(pipes_query)
    pipes_db = {p.id: p for p in result.scalars().all()}
    
    # Build order items with full pipe data
    order_items = []
    for item in request.items:
        pipe = pipes_db.get(item.pipe_id)
        if not pipe:
            logger.warning("calc.optimize.pipe_missing", extra={"pipe_id": item.pipe_id})
            raise HTTPException(404, f"Pipe ID {item.pipe_id} not found")
        
        order_items.append({
            "pipe_id": pipe.id,
            "code": pipe.code,
            "dn_mm": pipe.dn_mm,
            "sdr": pipe.sdr,
            "pn_class": pipe.pn_class,
            "inner_diameter_mm": float(pipe.inner_diameter_mm),
            "wall_mm": float(pipe.wall_mm),
            "weight_per_meter": float(pipe.weight_per_meter),
            "quantity": item.quantity
        })
    
    # Load truck config
    if request.truck_config_id:
        truck_query = select(TruckConfig).where(TruckConfig.id == request.truck_config_id)
    else:
        truck_query = select(TruckConfig).limit(1)
    
    truck = (await db.execute(truck_query)).scalar_one_or_none()
    
    truck_config = {
        "name": truck.name if truck else "Standard 24t Romania",
        "max_payload_kg": truck.max_payload_kg if truck else 24000,
        "internal_length_mm": truck.internal_length_mm if truck else 13600,
        "internal_width_mm": truck.internal_width_mm if truck else 2480,
        "internal_height_mm": truck.internal_height_mm if truck else 2700,
    }
    
    # Calculate loading plan
    # Calculate loading plan (run in threadpool to prevent blocking event loop)
    from fastapi.concurrency import run_in_threadpool
    plan = await run_in_threadpool(
        calculate_loading_plan,
        order_items,
        truck_config,
        request.pipe_length_m,
        request.enable_nesting,
        request.max_nesting_levels
    )
    
    result = loading_plan_to_dict(plan)
    logger.info(
        "calc.optimize.done",
        extra={"trucks": len(result.get("trucks", [])), "warnings": len(result.get("warnings", []))},
    )
    
    return OptimizeResponse(
        summary=result["summary"],
        trucks=result["trucks"],
        nesting_stats=result["nesting_stats"],
        weight_limits=result["weight_limits"],
        warnings=result["warnings"]
    )


@router.post("/validate-nesting", response_model=NestingValidationResponse)
async def validate_nesting(
    outer_pipe_id: int,
    inner_pipe_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate if inner pipe can be nested inside outer pipe.
    
    Uses formula: Gap_min = C_base + (Factor_diameter × DN_outer)
    Where C_base = 15mm, Factor = 0.015
    """
    # Load both pipes
    query = select(PipeCatalog).where(
        PipeCatalog.id.in_([outer_pipe_id, inner_pipe_id])
    )
    result = await db.execute(query)
    pipes = {p.id: p for p in result.scalars().all()}
    
    outer = pipes.get(outer_pipe_id)
    inner = pipes.get(inner_pipe_id)
    
    if not outer:
        logger.warning("calc.nesting.pipe_missing", extra={"pipe_id": outer_pipe_id, "role": "outer"})
        raise HTTPException(404, f"Outer pipe ID {outer_pipe_id} not found")
    if not inner:
        logger.warning("calc.nesting.pipe_missing", extra={"pipe_id": inner_pipe_id, "role": "inner"})
        raise HTTPException(404, f"Inner pipe ID {inner_pipe_id} not found")
    
    # Validate nesting
    result = validate_nesting_compatibility(
        host_inner_diameter_mm=float(outer.inner_diameter_mm),
        host_outer_diameter_mm=outer.dn_mm,
        guest_outer_diameter_mm=inner.dn_mm,
        apply_ovality=True
    )
    
    return NestingValidationResponse(
        is_valid=result.is_valid,
        outer_pipe={"id": outer.id, "code": outer.code, "dn_mm": outer.dn_mm},
        inner_pipe={"id": inner.id, "code": inner.code, "dn_mm": inner.dn_mm},
        gap_available_mm=round(result.available_gap_mm, 1),
        gap_required_mm=round(result.required_gap_mm, 1),
        message=result.message
    )


@router.get("/trucks/")
async def list_truck_configs(db: AsyncSession = Depends(get_db)):
    """List available truck configurations."""
    query = select(TruckConfig)
    result = await db.execute(query)
    trucks = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "max_payload_kg": t.max_payload_kg,
            "dimensions_mm": {
                "length": t.internal_length_mm,
                "width": t.internal_width_mm,
                "height": t.internal_height_mm
            }
        }
        for t in trucks
    ]
