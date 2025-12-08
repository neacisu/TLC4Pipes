"""
LoadingPlan Model - Optimized Loading Plans
"""

from typing import Any, List
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class LoadingPlan(Base, TimestampMixin):
    """
    Generated loading plan for a truck.
    
    Contains:
    - Truck number (for multi-truck orders)
    - Total weight and volume utilization
    - plan_data: JSON with detailed placement instructions
    """
    
    __tablename__ = "loading_plans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    truck_config_id: Mapped[int] = mapped_column(ForeignKey("truck_configs.id"))
    truck_number: Mapped[int] = mapped_column(Integer, default=1)
    total_weight_kg: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    volume_utilization: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    plan_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="loading_plans")
    truck_config: Mapped["TruckConfig"] = relationship("TruckConfig")
    nested_bundles: Mapped[List["NestedBundle"]] = relationship(
        "NestedBundle",
        back_populates="loading_plan",
        cascade="all, delete-orphan"
    )
    
    @property
    def weight_utilization_pct(self) -> float:
        """Calculate weight utilization percentage."""
        if self.truck_config and self.total_weight_kg:
            return (float(self.total_weight_kg) / self.truck_config.max_payload_kg) * 100
        return 0.0
    
    @property
    def is_overweight(self) -> bool:
        """Check if plan exceeds truck weight limit."""
        if self.truck_config and self.total_weight_kg:
            return float(self.total_weight_kg) > self.truck_config.max_payload_kg
        return False
    
    def __repr__(self) -> str:
        return f"<LoadingPlan truck#{self.truck_number} {self.total_weight_kg}kg>"


# Import at end to avoid circular imports
from app.models.order import Order
from app.models.truck_config import TruckConfig
from app.models.nested_bundle import NestedBundle
