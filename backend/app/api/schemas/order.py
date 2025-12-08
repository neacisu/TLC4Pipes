"""Order Pydantic Schemas"""

from uuid import UUID
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    """Schema for adding an item to an order."""
    pipe_id: int
    quantity: int = Field(..., ge=1, le=100000)


class OrderItemResponse(BaseModel):
    """Schema for order item response."""
    id: int
    pipe_id: int
    pipe_code: str
    quantity: int
    total_weight_kg: Optional[Decimal]
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    name: Optional[str] = Field(None, max_length=255)
    pipe_length_m: Decimal = Field(default=Decimal("12.0"), ge=6, le=16)
    items: List[OrderItemCreate] = []


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: UUID
    name: Optional[str]
    pipe_length_m: Decimal
    status: str
    total_weight_kg: Optional[Decimal]
    total_pipes: Optional[int]
    items: List[OrderItemResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True
