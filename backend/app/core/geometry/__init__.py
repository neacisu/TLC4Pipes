"""
Geometry Module

Provides geometric calculations for pipe stacking and visualization.
"""

from app.core.geometry.hexagonal_packing import (
    calculate_hexagonal_packing,
    calculate_stack_height_mm,
    calculate_max_rows,
    calculate_pipes_per_row,
    estimate_mixed_stack_height,
    PackingResult,
    PipePosition,
)
from app.core.geometry.stacking_calculator import (
    calculate_stack_dimensions,
    analyze_stack_stability,
    calculate_optimal_stacking,
    StackDimensions,
    StackAnalysis,
)
from app.core.geometry.center_of_gravity import (
    calculate_center_of_gravity,
    calculate_axle_loads,
    calculate_cog_from_truck_load,
    CenterOfGravityResult,
    AxleLoadResult,
    LoadItem,
)

__all__ = [
    # Hexagonal packing
    "calculate_hexagonal_packing",
    "calculate_stack_height_mm",
    "calculate_max_rows",
    "calculate_pipes_per_row",
    "estimate_mixed_stack_height",
    "PackingResult",
    "PipePosition",
    # Stacking
    "calculate_stack_dimensions",
    "analyze_stack_stability",
    "calculate_optimal_stacking",
    "StackDimensions",
    "StackAnalysis",
    # Center of gravity
    "calculate_center_of_gravity",
    "calculate_axle_loads",
    "calculate_cog_from_truck_load",
    "CenterOfGravityResult",
    "AxleLoadResult",
    "LoadItem",
]
