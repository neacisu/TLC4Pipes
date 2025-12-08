"""
Packing Configuration Model

Stores packing algorithm parameters and pipe specifications.
"""

from sqlalchemy import Boolean, Column, Integer, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.models.base import Base


class PackingConfig(Base):
    """Packing algorithm configuration."""
    
    __tablename__ = "packing_config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Profile identification
    name = Column(String(100), nullable=False, unique=True, default="default")
    description = Column(String(255))
    
    # Packing efficiency constants
    square_packing_efficiency = Column(Numeric(5, 4), default=0.785)   # π/4
    hexagonal_packing_efficiency = Column(Numeric(5, 4), default=0.907) # ~90.7%
    
    # Pipe range constraints
    min_pipe_dn_mm = Column(Integer, default=20)
    max_pipe_dn_mm = Column(Integer, default=1200)
    
    # Pipe lengths
    default_pipe_length_m = Column(Numeric(5, 2), default=12.0)
    available_lengths_m = Column(JSONB, default=[12.0, 12.5, 13.0])
    
    # Standard DN values
    standard_dn_values = Column(JSONB, default=[
        20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160,
        180, 200, 225, 250, 280, 315, 355, 400, 450, 500,
        560, 630, 710, 800, 900, 1000, 1200
    ])
    
    # Packing mode preference
    prefer_hexagonal = Column(Boolean, default=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<PackingConfig(name={self.name}, hex_eff={self.hexagonal_packing_efficiency})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "square_packing_efficiency": float(self.square_packing_efficiency) if self.square_packing_efficiency else None,
            "hexagonal_packing_efficiency": float(self.hexagonal_packing_efficiency) if self.hexagonal_packing_efficiency else None,
            "min_pipe_dn_mm": self.min_pipe_dn_mm,
            "max_pipe_dn_mm": self.max_pipe_dn_mm,
            "default_pipe_length_m": float(self.default_pipe_length_m) if self.default_pipe_length_m else None,
            "available_lengths_m": self.available_lengths_m,
            "standard_dn_values": self.standard_dn_values,
            "prefer_hexagonal": self.prefer_hexagonal,
            "is_active": self.is_active,
        }
