"""
Transport Limits Settings Model

Stores legal transport limits per region (RO, EU).
"""

from sqlalchemy import Boolean, Column, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func

from app.models.base import Base


class TransportLimits(Base):
    """Legal transport limits per region."""
    
    __tablename__ = "transport_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Region identification
    region_code = Column(String(10), nullable=False, unique=True)  # 'RO', 'EU'
    region_name = Column(String(100))  # 'Romania', 'European Union'
    
    # Weight limits (kg)
    max_payload_kg = Column(Integer, default=24000)
    max_total_vehicle_kg = Column(Integer, default=40000)
    max_axle_motor_kg = Column(Integer, default=11500)
    max_axle_trailer_kg = Column(Integer, default=8000)
    num_trailer_axles = Column(Integer, default=3)
    
    # Center of gravity optimal range (meters from front)
    optimal_cog_min_m = Column(Numeric(5, 2), default=5.5)
    optimal_cog_max_m = Column(Numeric(5, 2), default=7.5)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<TransportLimits(region={self.region_code}, payload={self.max_payload_kg}kg)>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "region_code": self.region_code,
            "region_name": self.region_name,
            "max_payload_kg": self.max_payload_kg,
            "max_total_vehicle_kg": self.max_total_vehicle_kg,
            "max_axle_motor_kg": self.max_axle_motor_kg,
            "max_axle_trailer_kg": self.max_axle_trailer_kg,
            "num_trailer_axles": self.num_trailer_axles,
            "optimal_cog_min_m": float(self.optimal_cog_min_m) if self.optimal_cog_min_m else None,
            "optimal_cog_max_m": float(self.optimal_cog_max_m) if self.optimal_cog_max_m else None,
            "is_active": self.is_active,
        }
