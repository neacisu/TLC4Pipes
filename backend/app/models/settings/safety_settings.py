"""
Safety Settings Model

Stores safety margins and securing requirements.
"""

from sqlalchemy import Boolean, Column, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func

from app.models.base import Base


class SafetySettings(Base):
    """Safety margins and securing requirements."""
    
    __tablename__ = "safety_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Profile identification
    name = Column(String(100), nullable=False, unique=True, default="default")
    description = Column(String(255))
    
    # Weight safety
    weight_margin_percent = Column(Numeric(5, 2), default=2.0)  # 2% buffer
    
    # Gap safety
    gap_margin_mm = Column(Numeric(6, 2), default=5.0)  # Additional clearance
    
    # Securing requirements (EN 12195)
    straps_per_tonne = Column(Numeric(5, 2), default=0.5)  # ~1 strap per 2t
    recommended_strap_force_dan = Column(Integer, default=500)  # STF 500daN
    require_anti_slip_mats = Column(Boolean, default=True)
    
    # Stack safety
    max_stack_height_factor = Column(Numeric(4, 2), default=0.9)  # 90% of truck height
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<SafetySettings(name={self.name}, weight_margin={self.weight_margin_percent}%)>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "weight_margin_percent": float(self.weight_margin_percent) if self.weight_margin_percent else None,
            "gap_margin_mm": float(self.gap_margin_mm) if self.gap_margin_mm else None,
            "straps_per_tonne": float(self.straps_per_tonne) if self.straps_per_tonne else None,
            "recommended_strap_force_dan": self.recommended_strap_force_dan,
            "require_anti_slip_mats": self.require_anti_slip_mats,
            "max_stack_height_factor": float(self.max_stack_height_factor) if self.max_stack_height_factor else None,
            "is_active": self.is_active,
        }
