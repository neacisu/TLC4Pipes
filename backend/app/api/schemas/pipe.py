"""Pipe Pydantic Schemas"""

from pydantic import BaseModel, Field


class PipeBase(BaseModel):
    """Base schema for pipe data."""
    dn_mm: int = Field(..., ge=20, le=1200, description="Nominal diameter in mm")
    pn_class: str = Field(..., description="Pressure class (PN6, PN8, PN10, PN16)")
    sdr: int = Field(..., ge=6, le=41, description="Standard Dimension Ratio")
    wall_mm: float = Field(..., gt=0, description="Wall thickness in mm")
    inner_diameter_mm: float = Field(..., gt=0, description="Inner diameter in mm")
    weight_per_meter: float = Field(..., gt=0, description="Weight in kg/m")


class PipeCreate(PipeBase):
    """Schema for creating a new pipe."""
    code: str = Field(..., max_length=50, description="Unique pipe code")


class PipeResponse(PipeBase):
    """Schema for pipe response."""
    id: int
    code: str
    
    class Config:
        from_attributes = True
