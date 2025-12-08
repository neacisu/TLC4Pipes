"""
Settings Seed Data

Populates all settings tables with default values from the specification.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.settings import (
    MaterialProperties,
    TransportLimits,
    NestingSettings,
    TruckDimensions,
    SafetySettings,
    PackingConfig,
)


async def seed_material_properties(session: AsyncSession):
    """Seed material properties table."""
    existing = await session.execute(
        select(MaterialProperties).where(MaterialProperties.material_type == "HDPE_PE100")
    )
    if existing.scalar_one_or_none():
        return
    
    materials = [
        MaterialProperties(
            material_type="HDPE_PE100",
            material_name="HDPE PE100 Standard",
            density_kg_m3=950,
            friction_coefficient=0.25,
        ),
        MaterialProperties(
            material_type="HDPE_PE80",
            material_name="HDPE PE80 Legacy",
            density_kg_m3=940,
            friction_coefficient=0.25,
        ),
    ]
    
    session.add_all(materials)
    await session.commit()
    print(f"  ✓ Seeded {len(materials)} material properties")


async def seed_transport_limits(session: AsyncSession):
    """Seed transport limits per region."""
    existing = await session.execute(
        select(TransportLimits).where(TransportLimits.region_code == "RO")
    )
    if existing.scalar_one_or_none():
        return
    
    limits = [
        TransportLimits(
            region_code="RO",
            region_name="Romania",
            max_payload_kg=24000,
            max_total_vehicle_kg=40000,
            max_axle_motor_kg=11500,
            max_axle_trailer_kg=8000,
            num_trailer_axles=3,
            optimal_cog_min_m=5.5,
            optimal_cog_max_m=7.5,
        ),
        TransportLimits(
            region_code="EU",
            region_name="European Union Standard",
            max_payload_kg=25000,
            max_total_vehicle_kg=44000,
            max_axle_motor_kg=11500,
            max_axle_trailer_kg=8000,
            num_trailer_axles=3,
            optimal_cog_min_m=5.5,
            optimal_cog_max_m=7.5,
        ),
    ]
    
    session.add_all(limits)
    await session.commit()
    print(f"  ✓ Seeded {len(limits)} transport limits")


async def seed_nesting_settings(session: AsyncSession):
    """Seed nesting algorithm settings."""
    existing = await session.execute(
        select(NestingSettings).where(NestingSettings.name == "default")
    )
    if existing.scalar_one_or_none():
        return
    
    settings = [
        NestingSettings(
            name="default",
            description="Standard nesting settings from specification",
            base_clearance_mm=15.0,
            diameter_factor=0.015,
            ovality_factor=0.04,
            max_nesting_levels=4,
            heavy_extraction_threshold_kg=2000,
            allow_mixed_sdr=True,
            prefer_same_sdr=True,
        ),
        NestingSettings(
            name="conservative",
            description="More safety margin, fewer nesting levels",
            base_clearance_mm=20.0,
            diameter_factor=0.02,
            ovality_factor=0.05,
            max_nesting_levels=3,
            heavy_extraction_threshold_kg=1500,
            allow_mixed_sdr=False,
            prefer_same_sdr=True,
        ),
    ]
    
    session.add_all(settings)
    await session.commit()
    print(f"  ✓ Seeded {len(settings)} nesting settings")


async def seed_truck_dimensions(session: AsyncSession):
    """Seed truck dimension templates."""
    existing = await session.execute(
        select(TruckDimensions).where(TruckDimensions.name == "Standard 24t")
    )
    if existing.scalar_one_or_none():
        return
    
    trucks = [
        TruckDimensions(
            name="Standard 24t",
            truck_type="standard",
            description="Standard 24t Romania semi-trailer",
            internal_length_mm=13600,
            internal_width_mm=2480,
            internal_height_mm=2700,
            kingpin_position_m=1.5,
            trailer_length_m=13.6,
            axle_group_position_m=12.1,
        ),
        TruckDimensions(
            name="Mega Trailer",
            truck_type="mega",
            description="Mega trailer with lowered floor",
            internal_length_mm=13600,
            internal_width_mm=2480,
            internal_height_mm=3000,
            kingpin_position_m=1.5,
            trailer_length_m=13.6,
            axle_group_position_m=12.1,
        ),
        TruckDimensions(
            name="Short Trailer",
            truck_type="standard",
            description="Shorter semi-trailer for urban delivery",
            internal_length_mm=12000,
            internal_width_mm=2480,
            internal_height_mm=2700,
            kingpin_position_m=1.3,
            trailer_length_m=12.0,
            axle_group_position_m=10.8,
        ),
    ]
    
    session.add_all(trucks)
    await session.commit()
    print(f"  ✓ Seeded {len(trucks)} truck dimensions")


async def seed_safety_settings(session: AsyncSession):
    """Seed safety margin settings."""
    existing = await session.execute(
        select(SafetySettings).where(SafetySettings.name == "default")
    )
    if existing.scalar_one_or_none():
        return
    
    settings = [
        SafetySettings(
            name="default",
            description="Standard safety margins from EN 12195",
            weight_margin_percent=2.0,
            gap_margin_mm=5.0,
            straps_per_tonne=0.5,
            recommended_strap_force_dan=500,
            require_anti_slip_mats=True,
            max_stack_height_factor=0.9,
        ),
        SafetySettings(
            name="strict",
            description="Stricter margins for long-distance transport",
            weight_margin_percent=5.0,
            gap_margin_mm=10.0,
            straps_per_tonne=0.7,
            recommended_strap_force_dan=750,
            require_anti_slip_mats=True,
            max_stack_height_factor=0.85,
        ),
    ]
    
    session.add_all(settings)
    await session.commit()
    print(f"  ✓ Seeded {len(settings)} safety settings")


async def seed_packing_config(session: AsyncSession):
    """Seed packing algorithm configuration."""
    existing = await session.execute(
        select(PackingConfig).where(PackingConfig.name == "default")
    )
    if existing.scalar_one_or_none():
        return
    
    configs = [
        PackingConfig(
            name="default",
            description="Standard packing configuration",
            square_packing_efficiency=0.785,
            hexagonal_packing_efficiency=0.907,
            min_pipe_dn_mm=20,
            max_pipe_dn_mm=1200,
            default_pipe_length_m=12.0,
            available_lengths_m=[12.0, 12.5, 13.0],
            standard_dn_values=[
                20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160,
                180, 200, 225, 250, 280, 315, 355, 400, 450, 500,
                560, 630, 710, 800, 900, 1000, 1200
            ],
            prefer_hexagonal=True,
        ),
    ]
    
    session.add_all(configs)
    await session.commit()
    print(f"  ✓ Seeded {len(configs)} packing configs")


async def seed_all_settings(session: AsyncSession):
    """Run all settings seeds."""
    print("Seeding settings tables...")
    await seed_material_properties(session)
    await seed_transport_limits(session)
    await seed_nesting_settings(session)
    await seed_truck_dimensions(session)
    await seed_safety_settings(session)
    await seed_packing_config(session)
    print("✓ All settings seeded successfully!")
