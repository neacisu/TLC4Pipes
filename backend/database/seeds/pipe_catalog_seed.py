"""
Pipe Catalog Seed Data

Seeds the pipe_catalog table with all HDPE pipe specifications.
Data from specification document - 4 SDR classes (PN6, PN8, PN10, PN16).
"""

import asyncio
from decimal import Decimal
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import async_session_maker
from app.models.pipe_catalog import PipeCatalog


# Complete HDPE pipe catalog data from specification document
PIPE_DATA = [
    # SDR 26 / PN6 - Thinnest walls
    {"code": "TPE020/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 20, "wall_mm": 2.0, "inner_diameter_mm": 16.0, "weight_per_meter": 0.12},
    {"code": "TPE025/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 25, "wall_mm": 2.0, "inner_diameter_mm": 21.0, "weight_per_meter": 0.15},
    {"code": "TPE032/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 32, "wall_mm": 2.0, "inner_diameter_mm": 28.0, "weight_per_meter": 0.19},
    {"code": "TPE040/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 40, "wall_mm": 2.0, "inner_diameter_mm": 36.0, "weight_per_meter": 0.24},
    {"code": "TPE050/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 50, "wall_mm": 2.0, "inner_diameter_mm": 46.0, "weight_per_meter": 0.31},
    {"code": "TPE063/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 63, "wall_mm": 2.5, "inner_diameter_mm": 58.0, "weight_per_meter": 0.48},
    {"code": "TPE075/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 75, "wall_mm": 2.9, "inner_diameter_mm": 69.2, "weight_per_meter": 0.67},
    {"code": "TPE090/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 90, "wall_mm": 3.5, "inner_diameter_mm": 83.0, "weight_per_meter": 0.97},
    {"code": "TPE110/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 110, "wall_mm": 4.2, "inner_diameter_mm": 101.6, "weight_per_meter": 1.42},
    {"code": "TPE125/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 125, "wall_mm": 4.8, "inner_diameter_mm": 115.4, "weight_per_meter": 1.83},
    {"code": "TPE140/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 140, "wall_mm": 5.4, "inner_diameter_mm": 129.2, "weight_per_meter": 2.31},
    {"code": "TPE160/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 160, "wall_mm": 6.2, "inner_diameter_mm": 147.6, "weight_per_meter": 3.03},
    {"code": "TPE180/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 180, "wall_mm": 6.9, "inner_diameter_mm": 166.2, "weight_per_meter": 3.78},
    {"code": "TPE200/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 200, "wall_mm": 7.7, "inner_diameter_mm": 184.6, "weight_per_meter": 4.73},
    {"code": "TPE225/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 225, "wall_mm": 8.6, "inner_diameter_mm": 207.8, "weight_per_meter": 5.93},
    {"code": "TPE250/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 250, "wall_mm": 9.6, "inner_diameter_mm": 230.8, "weight_per_meter": 7.34},
    {"code": "TPE280/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 280, "wall_mm": 10.7, "inner_diameter_mm": 258.6, "weight_per_meter": 9.16},
    {"code": "TPE315/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 315, "wall_mm": 12.1, "inner_diameter_mm": 290.8, "weight_per_meter": 11.71},
    {"code": "TPE355/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 355, "wall_mm": 13.6, "inner_diameter_mm": 327.8, "weight_per_meter": 14.79},
    {"code": "TPE400/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 400, "wall_mm": 15.3, "inner_diameter_mm": 369.4, "weight_per_meter": 18.80},
    {"code": "TPE450/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 450, "wall_mm": 17.2, "inner_diameter_mm": 415.6, "weight_per_meter": 23.72},
    {"code": "TPE500/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 500, "wall_mm": 19.1, "inner_diameter_mm": 461.8, "weight_per_meter": 29.34},
    {"code": "TPE560/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 560, "wall_mm": 21.4, "inner_diameter_mm": 517.2, "weight_per_meter": 36.81},
    {"code": "TPE630/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 630, "wall_mm": 24.1, "inner_diameter_mm": 581.8, "weight_per_meter": 46.64},
    {"code": "TPE710/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 710, "wall_mm": 27.2, "inner_diameter_mm": 655.6, "weight_per_meter": 59.28},
    {"code": "TPE800/PN6", "sdr": 26, "pn_class": "PN6", "dn_mm": 800, "wall_mm": 30.6, "inner_diameter_mm": 738.8, "weight_per_meter": 75.19},
    
    # SDR 21 / PN8
    {"code": "TPE020/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 20, "wall_mm": 2.0, "inner_diameter_mm": 16.0, "weight_per_meter": 0.12},
    {"code": "TPE025/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 25, "wall_mm": 2.0, "inner_diameter_mm": 21.0, "weight_per_meter": 0.15},
    {"code": "TPE032/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 32, "wall_mm": 2.0, "inner_diameter_mm": 28.0, "weight_per_meter": 0.19},
    {"code": "TPE040/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 40, "wall_mm": 2.0, "inner_diameter_mm": 36.0, "weight_per_meter": 0.24},
    {"code": "TPE050/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 50, "wall_mm": 2.4, "inner_diameter_mm": 45.2, "weight_per_meter": 0.37},
    {"code": "TPE063/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 63, "wall_mm": 3.0, "inner_diameter_mm": 57.0, "weight_per_meter": 0.57},
    {"code": "TPE075/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 75, "wall_mm": 3.6, "inner_diameter_mm": 67.8, "weight_per_meter": 0.82},
    {"code": "TPE090/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 90, "wall_mm": 4.3, "inner_diameter_mm": 81.4, "weight_per_meter": 1.17},
    {"code": "TPE110/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 110, "wall_mm": 5.3, "inner_diameter_mm": 99.4, "weight_per_meter": 1.77},
    {"code": "TPE125/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 125, "wall_mm": 6.0, "inner_diameter_mm": 113.0, "weight_per_meter": 2.27},
    {"code": "TPE140/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 140, "wall_mm": 6.7, "inner_diameter_mm": 126.6, "weight_per_meter": 2.83},
    {"code": "TPE160/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 160, "wall_mm": 7.7, "inner_diameter_mm": 144.6, "weight_per_meter": 3.74},
    {"code": "TPE180/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 180, "wall_mm": 8.6, "inner_diameter_mm": 162.8, "weight_per_meter": 4.68},
    {"code": "TPE200/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 200, "wall_mm": 9.6, "inner_diameter_mm": 180.8, "weight_per_meter": 5.83},
    {"code": "TPE225/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 225, "wall_mm": 10.8, "inner_diameter_mm": 203.4, "weight_per_meter": 7.38},
    {"code": "TPE250/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 250, "wall_mm": 11.9, "inner_diameter_mm": 226.2, "weight_per_meter": 9.02},
    {"code": "TPE280/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 280, "wall_mm": 13.4, "inner_diameter_mm": 253.2, "weight_per_meter": 11.38},
    {"code": "TPE315/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 315, "wall_mm": 15.0, "inner_diameter_mm": 285.0, "weight_per_meter": 14.36},
    {"code": "TPE355/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 355, "wall_mm": 16.9, "inner_diameter_mm": 321.2, "weight_per_meter": 18.19},
    {"code": "TPE400/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 400, "wall_mm": 19.1, "inner_diameter_mm": 361.8, "weight_per_meter": 23.17},
    {"code": "TPE450/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 450, "wall_mm": 21.5, "inner_diameter_mm": 407.0, "weight_per_meter": 29.38},
    {"code": "TPE500/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 500, "wall_mm": 23.9, "inner_diameter_mm": 452.2, "weight_per_meter": 36.29},
    {"code": "TPE560/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 560, "wall_mm": 26.7, "inner_diameter_mm": 506.6, "weight_per_meter": 45.36},
    {"code": "TPE630/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 630, "wall_mm": 30.0, "inner_diameter_mm": 570.0, "weight_per_meter": 57.32},
    {"code": "TPE710/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 710, "wall_mm": 33.9, "inner_diameter_mm": 642.2, "weight_per_meter": 73.06},
    {"code": "TPE800/PN8", "sdr": 21, "pn_class": "PN8", "dn_mm": 800, "wall_mm": 38.1, "inner_diameter_mm": 723.8, "weight_per_meter": 92.49},
    
    # SDR 17 / PN10
    {"code": "TPE020/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 20, "wall_mm": 2.0, "inner_diameter_mm": 16.0, "weight_per_meter": 0.12},
    {"code": "TPE025/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 25, "wall_mm": 2.0, "inner_diameter_mm": 21.0, "weight_per_meter": 0.15},
    {"code": "TPE032/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 32, "wall_mm": 2.0, "inner_diameter_mm": 28.0, "weight_per_meter": 0.19},
    {"code": "TPE040/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 40, "wall_mm": 2.4, "inner_diameter_mm": 35.2, "weight_per_meter": 0.29},
    {"code": "TPE050/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 50, "wall_mm": 3.0, "inner_diameter_mm": 44.0, "weight_per_meter": 0.45},
    {"code": "TPE063/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 63, "wall_mm": 3.8, "inner_diameter_mm": 55.4, "weight_per_meter": 0.72},
    {"code": "TPE075/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 75, "wall_mm": 4.5, "inner_diameter_mm": 66.0, "weight_per_meter": 1.01},
    {"code": "TPE090/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 90, "wall_mm": 5.4, "inner_diameter_mm": 79.2, "weight_per_meter": 1.45},
    {"code": "TPE110/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 110, "wall_mm": 6.6, "inner_diameter_mm": 96.8, "weight_per_meter": 2.18},
    {"code": "TPE125/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 125, "wall_mm": 7.4, "inner_diameter_mm": 110.2, "weight_per_meter": 2.77},
    {"code": "TPE140/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 140, "wall_mm": 8.3, "inner_diameter_mm": 123.4, "weight_per_meter": 3.48},
    {"code": "TPE160/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 160, "wall_mm": 9.5, "inner_diameter_mm": 141.0, "weight_per_meter": 4.56},
    {"code": "TPE180/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 180, "wall_mm": 10.7, "inner_diameter_mm": 158.6, "weight_per_meter": 5.77},
    {"code": "TPE200/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 200, "wall_mm": 11.9, "inner_diameter_mm": 176.2, "weight_per_meter": 7.14},
    {"code": "TPE225/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 225, "wall_mm": 13.4, "inner_diameter_mm": 198.2, "weight_per_meter": 9.04},
    {"code": "TPE250/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 250, "wall_mm": 14.8, "inner_diameter_mm": 220.4, "weight_per_meter": 11.10},
    {"code": "TPE280/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 280, "wall_mm": 16.6, "inner_diameter_mm": 246.8, "weight_per_meter": 13.95},
    {"code": "TPE315/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 315, "wall_mm": 18.7, "inner_diameter_mm": 277.6, "weight_per_meter": 17.68},
    {"code": "TPE355/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 355, "wall_mm": 21.1, "inner_diameter_mm": 312.8, "weight_per_meter": 22.47},
    {"code": "TPE400/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 400, "wall_mm": 23.7, "inner_diameter_mm": 352.6, "weight_per_meter": 28.47},
    {"code": "TPE450/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 450, "wall_mm": 26.7, "inner_diameter_mm": 396.6, "weight_per_meter": 36.04},
    {"code": "TPE500/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 500, "wall_mm": 29.7, "inner_diameter_mm": 440.6, "weight_per_meter": 44.60},
    {"code": "TPE560/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 560, "wall_mm": 33.2, "inner_diameter_mm": 493.6, "weight_per_meter": 55.76},
    {"code": "TPE630/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 630, "wall_mm": 37.4, "inner_diameter_mm": 555.2, "weight_per_meter": 70.75},
    {"code": "TPE710/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 710, "wall_mm": 42.1, "inner_diameter_mm": 625.8, "weight_per_meter": 89.73},
    {"code": "TPE800/PN10", "sdr": 17, "pn_class": "PN10", "dn_mm": 800, "wall_mm": 47.4, "inner_diameter_mm": 705.2, "weight_per_meter": 113.68},
    
    # SDR 11 / PN16 - Thickest walls, heaviest
    {"code": "TPE020/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 20, "wall_mm": 2.0, "inner_diameter_mm": 16.0, "weight_per_meter": 0.12},
    {"code": "TPE025/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 25, "wall_mm": 2.3, "inner_diameter_mm": 20.4, "weight_per_meter": 0.17},
    {"code": "TPE032/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 32, "wall_mm": 3.0, "inner_diameter_mm": 26.0, "weight_per_meter": 0.28},
    {"code": "TPE040/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 40, "wall_mm": 3.7, "inner_diameter_mm": 32.6, "weight_per_meter": 0.43},
    {"code": "TPE050/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 50, "wall_mm": 4.6, "inner_diameter_mm": 40.8, "weight_per_meter": 0.67},
    {"code": "TPE063/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 63, "wall_mm": 5.8, "inner_diameter_mm": 51.4, "weight_per_meter": 1.06},
    {"code": "TPE075/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 75, "wall_mm": 6.8, "inner_diameter_mm": 61.4, "weight_per_meter": 1.47},
    {"code": "TPE090/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 90, "wall_mm": 8.2, "inner_diameter_mm": 73.6, "weight_per_meter": 2.14},
    {"code": "TPE110/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 110, "wall_mm": 10.0, "inner_diameter_mm": 90.0, "weight_per_meter": 3.19},
    {"code": "TPE125/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 125, "wall_mm": 11.4, "inner_diameter_mm": 102.2, "weight_per_meter": 4.13},
    {"code": "TPE140/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 140, "wall_mm": 12.7, "inner_diameter_mm": 114.6, "weight_per_meter": 5.15},
    {"code": "TPE160/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 160, "wall_mm": 14.6, "inner_diameter_mm": 130.8, "weight_per_meter": 6.78},
    {"code": "TPE180/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 180, "wall_mm": 16.4, "inner_diameter_mm": 147.2, "weight_per_meter": 8.56},
    {"code": "TPE200/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 200, "wall_mm": 18.2, "inner_diameter_mm": 163.6, "weight_per_meter": 10.57},
    {"code": "TPE225/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 225, "wall_mm": 20.5, "inner_diameter_mm": 184.0, "weight_per_meter": 13.38},
    {"code": "TPE250/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 250, "wall_mm": 22.7, "inner_diameter_mm": 204.6, "weight_per_meter": 16.45},
    {"code": "TPE280/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 280, "wall_mm": 25.4, "inner_diameter_mm": 229.2, "weight_per_meter": 20.63},
    {"code": "TPE315/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 315, "wall_mm": 28.6, "inner_diameter_mm": 257.8, "weight_per_meter": 26.13},
    {"code": "TPE355/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 355, "wall_mm": 32.2, "inner_diameter_mm": 290.6, "weight_per_meter": 33.11},
    {"code": "TPE400/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 400, "wall_mm": 36.3, "inner_diameter_mm": 327.4, "weight_per_meter": 42.09},
    {"code": "TPE450/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 450, "wall_mm": 40.9, "inner_diameter_mm": 368.2, "weight_per_meter": 53.35},
    {"code": "TPE500/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 500, "wall_mm": 45.4, "inner_diameter_mm": 409.2, "weight_per_meter": 65.80},
    {"code": "TPE560/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 560, "wall_mm": 50.8, "inner_diameter_mm": 458.4, "weight_per_meter": 82.44},
    {"code": "TPE630/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 630, "wall_mm": 57.2, "inner_diameter_mm": 515.6, "weight_per_meter": 104.47},
    {"code": "TPE710/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 710, "wall_mm": 64.5, "inner_diameter_mm": 581.0, "weight_per_meter": 132.68},
    {"code": "TPE800/PN16", "sdr": 11, "pn_class": "PN16", "dn_mm": 800, "wall_mm": 72.6, "inner_diameter_mm": 654.8, "weight_per_meter": 168.70},
]


async def seed_pipe_catalog(session: AsyncSession) -> int:
    """
    Seed pipe catalog with HDPE specifications.
    
    Returns:
        Number of pipes inserted
    """
    # Check if already seeded
    result = await session.execute(select(PipeCatalog).limit(1))
    if result.scalar_one_or_none():
        print("Pipe catalog already seeded, skipping...")
        return 0
    
    count = 0
    for pipe_data in PIPE_DATA:
        pipe = PipeCatalog(
            code=pipe_data["code"],
            sdr=pipe_data["sdr"],
            pn_class=pipe_data["pn_class"],
            dn_mm=pipe_data["dn_mm"],
            wall_mm=Decimal(str(pipe_data["wall_mm"])),
            inner_diameter_mm=Decimal(str(pipe_data["inner_diameter_mm"])),
            weight_per_meter=Decimal(str(pipe_data["weight_per_meter"])),
        )
        session.add(pipe)
        count += 1
    
    await session.commit()
    print(f"✅ Seeded {count} pipes into pipe_catalog")
    return count


async def run_seed():
    """Run the seed function."""
    async with async_session_maker() as session:
        return await seed_pipe_catalog(session)


if __name__ == "__main__":
    asyncio.run(run_seed())
