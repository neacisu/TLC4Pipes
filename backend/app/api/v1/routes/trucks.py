"""
Trucks API Routes
Truck configuration endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database.connection import get_db
from app.models.truck_config import TruckConfig

router = APIRouter()


class TruckResponse(BaseModel):
    id: int
    name: str
    max_payload_kg: int
    internal_length_mm: int
    internal_width_mm: int
    internal_height_mm: int
    max_axle_weight_kg: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[TruckResponse])
async def list_trucks(db: AsyncSession = Depends(get_db)):
    """List all truck configurations."""
    query = select(TruckConfig)
    result = await db.execute(query)
    trucks = result.scalars().all()
    
    return [
        TruckResponse(
            id=t.id,
            name=t.name,
            max_payload_kg=t.max_payload_kg,
            internal_length_mm=t.internal_length_mm,
            internal_width_mm=t.internal_width_mm,
            internal_height_mm=t.internal_height_mm,
            max_axle_weight_kg=t.max_axle_weight_kg
        )
        for t in trucks
    ]


@router.get("/{truck_id}", response_model=TruckResponse)
async def get_truck(truck_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific truck configuration."""
    query = select(TruckConfig).where(TruckConfig.id == truck_id)
    result = await db.execute(query)
    truck = result.scalar_one_or_none()
    
    if not truck:
        raise HTTPException(status_code=404, detail="Truck configuration not found")
    
    return TruckResponse(
        id=truck.id,
        name=truck.name,
        max_payload_kg=truck.max_payload_kg,
        internal_length_mm=truck.internal_length_mm,
        internal_width_mm=truck.internal_width_mm,
        internal_height_mm=truck.internal_height_mm,
        max_axle_weight_kg=truck.max_axle_weight_kg
    )
