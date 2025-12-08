"""Truck Configuration Pydantic Schemas"""

from pydantic import BaseModel, Field


class TruckBase(BaseModel):
    """Base schema for truck configuration."""
    name: str = Field(..., max_length=100)
    max_payload_kg: int = Field(default=24000, ge=1000, le=50000)
    internal_length_mm: int = Field(default=13600, ge=5000, le=20000)
    internal_width_mm: int = Field(default=2480, ge=2000, le=3000)
    internal_height_mm: int = Field(default=3000, ge=2000, le=4000)
    axle_limit_kg: int = Field(default=11500, ge=5000, le=15000)


class TruckCreate(TruckBase):
    """Schema for creating a new truck configuration."""
    pass


class TruckResponse(TruckBase):
    """Schema for truck configuration response."""
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True
