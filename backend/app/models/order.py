"""
Order & OrderItem Models - Customer Orders
"""

from typing import List
from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Order(Base, TimestampMixin):
    """
    Customer order containing pipe items.
    
    Status: draft -> processing -> calculated -> completed
    """
    
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    pipe_length_m: Mapped[float] = mapped_column(Numeric(5, 2), default=12.0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    total_weight_kg: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    total_pipes: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Relationships
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    loading_plans: Mapped[List["LoadingPlan"]] = relationship(
        "LoadingPlan",
        back_populates="order"
    )
    
    def calculate_totals(self) -> None:
        """Recalculate total weight and pipe count from items."""
        self.total_pipes = sum(item.quantity for item in self.items)
        self.total_weight_kg = sum(
            float(item.line_weight_kg or 0) for item in self.items
        )
    
    def __repr__(self) -> str:
        return f"<Order {self.order_number} status={self.status}>"


class OrderItem(Base, TimestampMixin):
    """Single line item in an order - represents quantity of a specific pipe."""
    
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    pipe_id: Mapped[int] = mapped_column(ForeignKey("pipe_catalog.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    ordered_meters: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True, comment="Original meters ordered (unrounded)")
    pipe_count: Mapped[int] = mapped_column(Integer, nullable=True, comment="Number of pipes after rounding up")
    line_weight_kg: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    pipe: Mapped["PipeCatalog"] = relationship("PipeCatalog")
    
    def calculate_weight(self, pipe_length_m: float) -> None:
        """Calculate total line weight based on pipe specs and order length."""
        if self.pipe:
            self.line_weight_kg = (
                float(self.pipe.weight_per_meter) * 
                pipe_length_m * 
                self.quantity
            )
    
    def __repr__(self) -> str:
        return f"<OrderItem pipe_id={self.pipe_id} qty={self.quantity}>"


# Import at end to avoid circular imports
from app.models.loading_plan import LoadingPlan
from app.models.pipe_catalog import PipeCatalog
