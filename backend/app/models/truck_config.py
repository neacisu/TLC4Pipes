"""
TruckConfig Model - Truck/Trailer Specifications
"""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TruckConfig(Base):
    """
    Truck/Trailer configuration for loading calculations.
    
    Default configurations:
    - Standard 24t Romania: 13.6m x 2.48m x 2.7m
    - Mega Trailer Romania: 13.6m x 2.48m x 3.0m
    """
    
    __tablename__ = "truck_configs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    max_payload_kg: Mapped[int] = mapped_column(Integer, default=24000)
    internal_length_mm: Mapped[int] = mapped_column(Integer, nullable=False)
    internal_width_mm: Mapped[int] = mapped_column(Integer, nullable=False)
    internal_height_mm: Mapped[int] = mapped_column(Integer, nullable=False)
    max_axle_weight_kg: Mapped[int] = mapped_column(Integer, default=11500)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    @property
    def internal_volume_m3(self) -> float:
        """Calculate internal volume in cubic meters."""
        return (
            self.internal_length_mm * 
            self.internal_width_mm * 
            self.internal_height_mm
        ) / 1_000_000_000  # mm³ to m³
    
    @property
    def cross_section_area_mm2(self) -> float:
        """Cross-sectional area for 2D packing calculations."""
        return self.internal_width_mm * self.internal_height_mm
    
    def __repr__(self) -> str:
        return f"<TruckConfig {self.name} {self.max_payload_kg}kg>"
