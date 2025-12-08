"""
PipeCatalog Model - HDPE Pipe Specifications
"""

from datetime import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PipeCatalog(Base):
    """
    HDPE Pipe catalog entry.
    
    Contains specifications for each pipe type including:
    - SDR (Standard Dimension Ratio): 11, 17, 21, 26
    - PN (Pressure Class): PN6, PN8, PN10, PN16
    - Physical dimensions and weight
    """
    
    __tablename__ = "pipe_catalog"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    sdr: Mapped[int] = mapped_column(Integer, nullable=False)
    pn_class: Mapped[str] = mapped_column(String(10), nullable=False)
    dn_mm: Mapped[int] = mapped_column(Integer, nullable=False)
    wall_mm: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    inner_diameter_mm: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    weight_per_meter: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=True
    )
    
    @property
    def outer_diameter_mm(self) -> float:
        """Calculate outer diameter from inner + wall thickness."""
        return float(self.inner_diameter_mm) + (2 * float(self.wall_mm))
    
    def weight_for_length(self, length_m: float) -> float:
        """Calculate total weight for a given pipe length."""
        return float(self.weight_per_meter) * length_m
    
    def __repr__(self) -> str:
        return f"<PipeCatalog {self.code} DN{self.dn_mm} SDR{self.sdr}>"
