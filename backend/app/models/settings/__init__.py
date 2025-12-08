"""
Settings Models Package

All configurable settings stored in database tables.
"""

from app.models.settings.material_properties import MaterialProperties
from app.models.settings.transport_limits import TransportLimits
from app.models.settings.nesting_settings import NestingSettings
from app.models.settings.truck_dimensions import TruckDimensions
from app.models.settings.safety_settings import SafetySettings
from app.models.settings.packing_config import PackingConfig

__all__ = [
    "MaterialProperties",
    "TransportLimits",
    "NestingSettings",
    "TruckDimensions",
    "SafetySettings",
    "PackingConfig",
]
