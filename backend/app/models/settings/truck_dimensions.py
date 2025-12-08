"""
Truck Dimensions Settings Model

Stores internal dimensions for different truck types.
Note: This extends TruckConfig with more detailed dimension settings.
"""

from sqlalchemy import Boolean, Column, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func

from app.models.base import Base


class TruckDimensions(Base):
    """Detailed truck dimension settings templates."""
    
    __tablename__ = "truck_dimensions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    name = Column(String(100), nullable=False, unique=True)
    truck_type = Column(String(50))  # 'standard', 'mega', 'curtainsider'
    description = Column(String(255))
    
    # Internal dimensions (mm)
    internal_length_mm = Column(Integer, default=13600)
    internal_width_mm = Column(Integer, default=2480)
    internal_height_mm = Column(Integer, default=2700)
    
    # Axle positions (m from front of trailer)
    kingpin_position_m = Column(Numeric(5, 2), default=1.5)
    trailer_length_m = Column(Numeric(5, 2), default=13.6)
    axle_group_position_m = Column(Numeric(5, 2), default=12.1)  # From front
    
    # Loading constraints
    max_floor_load_kg_m2 = Column(Integer, nullable=True)  # Floor load limit if any
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<TruckDimensions(name={self.name}, type={self.truck_type})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "truck_type": self.truck_type,
            "description": self.description,
            "internal_length_mm": self.internal_length_mm,
            "internal_width_mm": self.internal_width_mm,
            "internal_height_mm": self.internal_height_mm,
            "kingpin_position_m": float(self.kingpin_position_m) if self.kingpin_position_m else None,
            "trailer_length_m": float(self.trailer_length_m) if self.trailer_length_m else None,
            "axle_group_position_m": float(self.axle_group_position_m) if self.axle_group_position_m else None,
            "max_floor_load_kg_m2": self.max_floor_load_kg_m2,
            "is_active": self.is_active,
        }
