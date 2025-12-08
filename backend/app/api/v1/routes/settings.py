"""
Settings API Routes

CRUD endpoints for managing application settings.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from app.services.settings_service import (
    get_all_settings,
    get_material_properties,
    get_transport_limits,
    get_nesting_settings,
    get_truck_dimensions,
    get_safety_settings,
    get_packing_config,
    list_all_by_category,
    update_setting,
)


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_settings_overview(db: AsyncSession = Depends(get_db)):
    """
    Get all active settings in a single response.
    
    Returns default active setting from each category.
    """
    settings = await get_all_settings(db)
    logger.debug("settings.overview", extra={"count": len(settings) if settings else 0})
    return {"settings": settings}


@router.get("/material")
async def list_material_properties(db: AsyncSession = Depends(get_db)):
    """List all material property configurations."""
    items = await list_all_by_category(db, "material")
    return {"materials": items}


@router.get("/material/{material_type}")
async def get_material(
    material_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific material properties."""
    material = await get_material_properties(db, material_type)
    if not material:
        logger.warning("settings.material.not_found", extra={"material_type": material_type})
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.get("/transport")
async def list_transport_limits(db: AsyncSession = Depends(get_db)):
    """List all transport limit configurations."""
    items = await list_all_by_category(db, "transport")
    return {"regions": items}


@router.get("/transport/{region_code}")
async def get_transport(
    region_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get transport limits for a specific region."""
    limits = await get_transport_limits(db, region_code)
    if not limits:
        logger.warning("settings.transport.not_found", extra={"region_code": region_code})
        raise HTTPException(status_code=404, detail="Region not found")
    return limits


@router.get("/nesting")
async def list_nesting_settings(db: AsyncSession = Depends(get_db)):
    """List all nesting algorithm settings."""
    items = await list_all_by_category(db, "nesting")
    return {"profiles": items}


@router.get("/nesting/{name}")
async def get_nesting(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific nesting settings profile."""
    settings = await get_nesting_settings(db, name)
    if not settings:
        logger.warning("settings.nesting.not_found", extra={"name": name})
        raise HTTPException(status_code=404, detail="Nesting profile not found")
    return settings


@router.get("/truck-dimensions")
async def list_truck_dimensions(db: AsyncSession = Depends(get_db)):
    """List all truck dimension templates."""
    items = await list_all_by_category(db, "truck")
    return {"trucks": items}


@router.get("/truck-dimensions/{name}")
async def get_truck(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific truck dimensions."""
    truck = await get_truck_dimensions(db, name)
    if not truck:
        logger.warning("settings.truck.not_found", extra={"name": name})
        raise HTTPException(status_code=404, detail="Truck template not found")
    return truck


@router.get("/safety")
async def list_safety_settings(db: AsyncSession = Depends(get_db)):
    """List all safety margin settings."""
    items = await list_all_by_category(db, "safety")
    return {"profiles": items}


@router.get("/safety/{name}")
async def get_safety(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific safety settings profile."""
    settings = await get_safety_settings(db, name)
    if not settings:
        logger.warning("settings.safety.not_found", extra={"name": name})
        raise HTTPException(status_code=404, detail="Safety profile not found")
    return settings


@router.get("/packing")
async def list_packing_configs(db: AsyncSession = Depends(get_db)):
    """List all packing configurations."""
    items = await list_all_by_category(db, "packing")
    return {"configs": items}


@router.get("/packing/{name}")
async def get_packing(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific packing configuration."""
    config = await get_packing_config(db, name)
    if not config:
        logger.warning("settings.packing.not_found", extra={"name": name})
        raise HTTPException(status_code=404, detail="Packing config not found")
    return config


@router.patch("/{category}/{setting_id}")
async def update_setting_endpoint(
    category: str,
    setting_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific setting by category and ID.
    
    Categories: material, transport, nesting, truck, safety, packing
    """
    valid_categories = ["material", "transport", "nesting", "truck", "safety", "packing"]
    if category not in valid_categories:
        logger.warning("settings.update.invalid_category", extra={"category": category})
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {valid_categories}"
        )
    
    result = await update_setting(db, category, setting_id, data)
    if not result:
        logger.warning("settings.update.not_found", extra={"category": category, "setting_id": setting_id})
        raise HTTPException(status_code=404, detail="Setting not found")
    
    logger.info("settings.update.success", extra={"category": category, "setting_id": setting_id})
    return {"message": "Setting updated", "setting": result}
