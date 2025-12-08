"""
NestedBundle Model - Telescoped Pipe Bundles
"""

from typing import Any
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class NestedBundle(Base, TimestampMixin):
    """
    A telescoped bundle of pipes (Matryoshka pattern).
    
    Example:
    - outer_pipe: TPE630/PN6
    - nested_pipes: [TPE400/PN10, TPE315/PN6, TPE110/PN6]
    - nesting_levels: 3
    
    The outer pipe contains one or more inner pipes,
    which may themselves contain even smaller pipes.
    """
    
    __tablename__ = "nested_bundles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    loading_plan_id: Mapped[int] = mapped_column(
        ForeignKey("loading_plans.id", ondelete="CASCADE")
    )
    outer_pipe_id: Mapped[int] = mapped_column(ForeignKey("pipe_catalog.id"))
    bundle_weight_kg: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    nesting_levels: Mapped[int] = mapped_column(Integer, default=1)
    nested_pipes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    loading_plan: Mapped["LoadingPlan"] = relationship(
        "LoadingPlan",
        back_populates="nested_bundles"
    )
    outer_pipe: Mapped["PipeCatalog"] = relationship("PipeCatalog")
    
    @property
    def extraction_warning(self) -> bool:
        """
        Check if bundle requires heavy equipment for extraction.
        Threshold: 2000 kg (from specification document).
        """
        if self.bundle_weight_kg:
            return float(self.bundle_weight_kg) > 2000
        return False
    
    def __repr__(self) -> str:
        return f"<NestedBundle outer={self.outer_pipe_id} levels={self.nesting_levels}>"


# Import at end to avoid circular imports
from app.models.loading_plan import LoadingPlan
from app.models.pipe_catalog import PipeCatalog
