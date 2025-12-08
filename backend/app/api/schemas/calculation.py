"""Calculation Pydantic Schemas"""

from uuid import UUID
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class NestingValidation(BaseModel):
    """Schema for nesting validation result."""
    is_valid: bool
    gap_available_mm: Decimal
    gap_required_mm: Decimal
    message: str


class NestedBundle(BaseModel):
    """Schema for a nested pipe bundle."""
    outer_pipe_code: str
    outer_pipe_id: int
    inner_pipes: List[dict]
    total_weight_kg: Decimal
    nesting_levels: int


class TruckLoading(BaseModel):
    """Schema for a single truck's loading."""
    truck_number: int
    bundles: List[NestedBundle]
    total_weight_kg: Decimal
    weight_utilization_percent: Decimal
    volume_utilization_percent: Decimal
    center_of_gravity_x_mm: Optional[Decimal]


class CalculationRequest(BaseModel):
    """Schema for calculation request."""
    order_id: UUID
    truck_config_id: int = Field(default=1)
    optimize_for: str = Field(default="weight", description="'weight' or 'volume'")


class CalculationResponse(BaseModel):
    """Schema for calculation response."""
    order_id: UUID
    total_trucks: int
    trucks: List[TruckLoading]
    total_weight_kg: Decimal
    efficiency_mass: Decimal = Field(description="Mass utilization percentage")
    efficiency_volume: Decimal = Field(description="Volume utilization percentage")
