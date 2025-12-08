"""
Truck Configurations Seed Data

Seeds truck_configs table with standard truck types for Romania.
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import async_session_maker
from app.models.truck_config import TruckConfig


# Truck configurations for Romania transport
TRUCK_CONFIGS = [
    {
        "name": "Standard 24t Romania",
        "max_payload_kg": 24000,
        "internal_length_mm": 13600,
        "internal_width_mm": 2480,
        "internal_height_mm": 2700,
        "max_axle_weight_kg": 11500,
    },
    {
        "name": "Mega Trailer Romania",
        "max_payload_kg": 24000,
        "internal_length_mm": 13600,
        "internal_width_mm": 2480,
        "internal_height_mm": 3000,  # 30cm taller than standard
        "max_axle_weight_kg": 11500,
    },
    {
        "name": "Standard 24t EU",
        "max_payload_kg": 24000,
        "internal_length_mm": 13600,
        "internal_width_mm": 2450,
        "internal_height_mm": 2700,
        "max_axle_weight_kg": 11500,
    },
]


async def seed_truck_configs(session: AsyncSession) -> int:
    """
    Seed truck configurations.
    
    Returns:
        Number of trucks inserted
    """
    # Check if already seeded
    result = await session.execute(select(TruckConfig).limit(1))
    if result.scalar_one_or_none():
        print("Truck configs already seeded, skipping...")
        return 0
    
    count = 0
    for config_data in TRUCK_CONFIGS:
        config = TruckConfig(**config_data)
        session.add(config)
        count += 1
    
    await session.commit()
    print(f"✅ Seeded {count} truck configurations")
    return count


async def run_seed():
    """Run the seed function."""
    async with async_session_maker() as session:
        return await seed_truck_configs(session)


if __name__ == "__main__":
    asyncio.run(run_seed())
