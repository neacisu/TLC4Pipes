"""
Material Properties Settings Model

Stores physical properties for materials like HDPE.
"""

from sqlalchemy import Boolean, Column, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func

from app.models.base import Base


class MaterialProperties(Base):
    """Physical properties for materials."""
    
    __tablename__ = "material_properties"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Material identification
    material_type = Column(String(50), nullable=False, unique=True)  # 'HDPE_PE100'
    material_name = Column(String(100))  # 'HDPE PE100 Standard'
    
    # Physical properties
    density_kg_m3 = Column(Numeric(10, 2), default=950)
    friction_coefficient = Column(Numeric(5, 3), default=0.25)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<MaterialProperties(type={self.material_type}, density={self.density_kg_m3})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "material_type": self.material_type,
            "material_name": self.material_name,
            "density_kg_m3": float(self.density_kg_m3) if self.density_kg_m3 else None,
            "friction_coefficient": float(self.friction_coefficient) if self.friction_coefficient else None,
            "is_active": self.is_active,
        }
