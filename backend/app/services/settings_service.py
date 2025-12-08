"""
Settings Service

CRUD operations for all settings tables with caching support.
"""

from typing import Dict, Any, Optional, Type
from functools import lru_cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import (
    MaterialProperties,
    TransportLimits,
    NestingSettings,
    TruckDimensions,
    SafetySettings,
    PackingConfig,
)


# In-memory cache for settings (refreshed on demand)
_settings_cache: Dict[str, Dict[str, Any]] = {}


async def get_material_properties(
    session: AsyncSession,
    material_type: str = "HDPE_PE100"
) -> Optional[Dict[str, Any]]:
    """Get material properties by type."""
    query = select(MaterialProperties).where(
        MaterialProperties.material_type == material_type,
        MaterialProperties.is_active == True
    )
    result = await session.execute(query)
    material = result.scalar_one_or_none()
    return material.to_dict() if material else None


async def get_transport_limits(
    session: AsyncSession,
    region_code: str = "RO"
) -> Optional[Dict[str, Any]]:
    """Get transport limits by region."""
    query = select(TransportLimits).where(
        TransportLimits.region_code == region_code,
        TransportLimits.is_active == True
    )
    result = await session.execute(query)
    limits = result.scalar_one_or_none()
    return limits.to_dict() if limits else None


async def get_nesting_settings(
    session: AsyncSession,
    name: str = "default"
) -> Optional[Dict[str, Any]]:
    """Get nesting settings by name."""
    query = select(NestingSettings).where(
        NestingSettings.name == name,
        NestingSettings.is_active == True
    )
    result = await session.execute(query)
    settings = result.scalar_one_or_none()
    return settings.to_dict() if settings else None


async def get_truck_dimensions(
    session: AsyncSession,
    name: str = "Standard 24t"
) -> Optional[Dict[str, Any]]:
    """Get truck dimensions by name."""
    query = select(TruckDimensions).where(
        TruckDimensions.name == name,
        TruckDimensions.is_active == True
    )
    result = await session.execute(query)
    truck = result.scalar_one_or_none()
    return truck.to_dict() if truck else None


async def get_safety_settings(
    session: AsyncSession,
    name: str = "default"
) -> Optional[Dict[str, Any]]:
    """Get safety settings by name."""
    query = select(SafetySettings).where(
        SafetySettings.name == name,
        SafetySettings.is_active == True
    )
    result = await session.execute(query)
    settings = result.scalar_one_or_none()
    return settings.to_dict() if settings else None


async def get_packing_config(
    session: AsyncSession,
    name: str = "default"
) -> Optional[Dict[str, Any]]:
    """Get packing config by name."""
    query = select(PackingConfig).where(
        PackingConfig.name == name,
        PackingConfig.is_active == True
    )
    result = await session.execute(query)
    config = result.scalar_one_or_none()
    return config.to_dict() if config else None


async def get_all_settings(session: AsyncSession) -> Dict[str, Any]:
    """Get all active settings in a single dict."""
    return {
        "material": await get_material_properties(session),
        "transport": await get_transport_limits(session),
        "nesting": await get_nesting_settings(session),
        "truck": await get_truck_dimensions(session),
        "safety": await get_safety_settings(session),
        "packing": await get_packing_config(session),
    }


async def list_all_by_category(
    session: AsyncSession,
    category: str
) -> list:
    """List all entries for a specific category."""
    model_map = {
        "material": MaterialProperties,
        "transport": TransportLimits,
        "nesting": NestingSettings,
        "truck": TruckDimensions,
        "safety": SafetySettings,
        "packing": PackingConfig,
    }
    
    model = model_map.get(category)
    if not model:
        return []
    
    query = select(model)
    result = await session.execute(query)
    items = result.scalars().all()
    return [item.to_dict() for item in items]


async def update_setting(
    session: AsyncSession,
    category: str,
    setting_id: int,
    data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Update a specific setting by ID."""
    model_map = {
        "material": MaterialProperties,
        "transport": TransportLimits,
        "nesting": NestingSettings,
        "truck": TruckDimensions,
        "safety": SafetySettings,
        "packing": PackingConfig,
    }
    
    model = model_map.get(category)
    if not model:
        return None
    
    query = select(model).where(model.id == setting_id)
    result = await session.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        return None
    
    # Update fields
    for key, value in data.items():
        if hasattr(item, key) and key not in ("id", "created_at"):
            setattr(item, key, value)
    
    await session.commit()
    await session.refresh(item)
    
    # Clear cache
    _settings_cache.clear()
    
    return item.to_dict()


# Helper to get constants with fallbacks
def get_default_constants() -> Dict[str, Any]:
    """
    Get default constant values (fallback when DB not available).
    Used for backward compatibility with hardcoded constants.
    """
    return {
        # Material
        "HDPE_DENSITY_KG_M3": 950,
        "HDPE_FRICTION_COEFFICIENT": 0.25,
        
        # Transport
        "MAX_PAYLOAD_KG": 24000,
        "MAX_TOTAL_VEHICLE_KG": 40000,
        "MAX_AXLE_WEIGHT_MOTOR_KG": 11500,
        "MAX_AXLE_WEIGHT_TRAILER_KG": 8000,
        "OPTIMAL_COG_MIN_M": 5.5,
        "OPTIMAL_COG_MAX_M": 7.5,
        
        # Nesting
        "BASE_CLEARANCE_MM": 15.0,
        "DIAMETER_FACTOR": 0.015,
        "OVALITY_FACTOR": 0.04,
        "MAX_NESTING_LEVELS": 4,
        "HEAVY_EXTRACTION_THRESHOLD_KG": 2000,
        
        # Truck
        "STANDARD_TRUCK_LENGTH_MM": 13600,
        "STANDARD_TRUCK_WIDTH_MM": 2480,
        "STANDARD_TRUCK_HEIGHT_MM": 2700,
        "MEGA_TRUCK_HEIGHT_MM": 3000,
        "KINGPIN_POSITION_M": 1.5,
        
        # Safety
        "WEIGHT_SAFETY_MARGIN_PERCENT": 2.0,
        "GAP_SAFETY_MARGIN_MM": 5.0,
        
        # Packing
        "SQUARE_PACKING_EFFICIENCY": 0.785,
        "HEXAGONAL_PACKING_EFFICIENCY": 0.907,
        "DEFAULT_PIPE_LENGTH_M": 12.0,
    }
