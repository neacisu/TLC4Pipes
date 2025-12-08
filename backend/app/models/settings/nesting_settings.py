"""
Nesting Settings Model

Stores parameters for pipe nesting/telescoping algorithm.
"""

from sqlalchemy import Boolean, Column, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func

from app.models.base import Base


class NestingSettings(Base):
    """Settings for pipe nesting algorithm."""
    
    __tablename__ = "nesting_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Profile identification
    name = Column(String(100), nullable=False, unique=True, default="default")
    description = Column(String(255))
    
    # Gap clearance parameters
    base_clearance_mm = Column(Numeric(6, 2), default=15.0)  # Minimum absolute gap
    diameter_factor = Column(Numeric(6, 4), default=0.015)   # 1.5% for ovality
    ovality_factor = Column(Numeric(6, 4), default=0.04)     # 4% max ovality
    
    # Nesting limits
    max_nesting_levels = Column(Integer, default=4)
    heavy_extraction_threshold_kg = Column(Integer, default=2000)
    
    # SDR compatibility rules
    allow_mixed_sdr = Column(Boolean, default=True)
    prefer_same_sdr = Column(Boolean, default=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<NestingSettings(name={self.name}, max_levels={self.max_nesting_levels})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "base_clearance_mm": float(self.base_clearance_mm) if self.base_clearance_mm else None,
            "diameter_factor": float(self.diameter_factor) if self.diameter_factor else None,
            "ovality_factor": float(self.ovality_factor) if self.ovality_factor else None,
            "max_nesting_levels": self.max_nesting_levels,
            "heavy_extraction_threshold_kg": self.heavy_extraction_threshold_kg,
            "allow_mixed_sdr": self.allow_mixed_sdr,
            "prefer_same_sdr": self.prefer_same_sdr,
            "is_active": self.is_active,
        }
