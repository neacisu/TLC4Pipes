"""
Unit Converters and Calculation Utilities

Conversion functions for dimensions, weights, and volumes.
"""

import math
from typing import Tuple


def mm_to_m(mm: float) -> float:
    """Convert millimeters to meters."""
    return mm / 1000.0


def m_to_mm(m: float) -> float:
    """Convert meters to millimeters."""
    return m * 1000.0


def kg_to_tonnes(kg: float) -> float:
    """Convert kilograms to metric tonnes."""
    return kg / 1000.0


def tonnes_to_kg(tonnes: float) -> float:
    """Convert metric tonnes to kilograms."""
    return tonnes * 1000.0


def mm2_to_m2(mm2: float) -> float:
    """Convert square millimeters to square meters."""
    return mm2 / 1_000_000.0


def m2_to_mm2(m2: float) -> float:
    """Convert square meters to square millimeters."""
    return m2 * 1_000_000.0


def mm3_to_m3(mm3: float) -> float:
    """Convert cubic millimeters to cubic meters."""
    return mm3 / 1_000_000_000.0


def m3_to_mm3(m3: float) -> float:
    """Convert cubic meters to cubic millimeters."""
    return m3 * 1_000_000_000.0


def calculate_circle_area_mm2(diameter_mm: float) -> float:
    """Calculate area of a circle given diameter in mm."""
    radius = diameter_mm / 2.0
    return math.pi * radius * radius


def calculate_pipe_cross_section_area_mm2(
    outer_diameter_mm: float,
    inner_diameter_mm: float
) -> float:
    """Calculate cross-sectional area of pipe wall (ring area)."""
    outer_area = calculate_circle_area_mm2(outer_diameter_mm)
    inner_area = calculate_circle_area_mm2(inner_diameter_mm)
    return outer_area - inner_area


def calculate_pipe_volume_m3(
    outer_diameter_mm: float,
    inner_diameter_mm: float,
    length_m: float
) -> float:
    """Calculate volume of pipe material in cubic meters."""
    cross_section_mm2 = calculate_pipe_cross_section_area_mm2(
        outer_diameter_mm, inner_diameter_mm
    )
    length_mm = m_to_mm(length_m)
    volume_mm3 = cross_section_mm2 * length_mm
    return mm3_to_m3(volume_mm3)


def calculate_pipe_internal_volume_m3(
    inner_diameter_mm: float,
    length_m: float
) -> float:
    """Calculate internal (hollow) volume of pipe in cubic meters."""
    inner_area_mm2 = calculate_circle_area_mm2(inner_diameter_mm)
    length_mm = m_to_mm(length_m)
    volume_mm3 = inner_area_mm2 * length_mm
    return mm3_to_m3(volume_mm3)


def calculate_wall_thickness_mm(
    outer_diameter_mm: float,
    sdr: int
) -> float:
    """Calculate wall thickness from SDR formula: wall = OD / SDR."""
    return outer_diameter_mm / sdr


def calculate_inner_diameter_mm(
    outer_diameter_mm: float,
    wall_thickness_mm: float
) -> float:
    """Calculate inner diameter from outer diameter and wall thickness."""
    return outer_diameter_mm - (2 * wall_thickness_mm)


def calculate_outer_diameter_mm(
    inner_diameter_mm: float,
    wall_thickness_mm: float
) -> float:
    """Calculate outer diameter from inner diameter and wall thickness."""
    return inner_diameter_mm + (2 * wall_thickness_mm)


def calculate_pipe_weight_kg(
    weight_per_meter: float,
    length_m: float,
    quantity: int = 1
) -> float:
    """Calculate total weight of pipes."""
    return weight_per_meter * length_m * quantity


def format_weight_kg(weight_kg: float, precision: int = 2) -> str:
    """Format weight with appropriate unit (kg or tonnes)."""
    if weight_kg >= 1000:
        return f"{kg_to_tonnes(weight_kg):.{precision}f} t"
    return f"{weight_kg:.{precision}f} kg"


def format_dimension_mm(dimension_mm: float, precision: int = 1) -> str:
    """Format dimension with appropriate unit (mm or m)."""
    if dimension_mm >= 1000:
        return f"{mm_to_m(dimension_mm):.{precision}f} m"
    return f"{dimension_mm:.{precision}f} mm"


def calculate_hexagonal_stack_height_mm(
    pipe_diameter_mm: float,
    num_rows: int
) -> float:
    """
    Calculate height of hexagonal (staggered) pipe stack.
    
    Formula: H = D + (n-1) × D × (√3/2)
    Where D is diameter and n is number of rows.
    """
    if num_rows <= 0:
        return 0.0
    if num_rows == 1:
        return pipe_diameter_mm
    return pipe_diameter_mm + (num_rows - 1) * pipe_diameter_mm * (math.sqrt(3) / 2)


def calculate_max_hexagonal_rows(
    pipe_diameter_mm: float,
    available_height_mm: float
) -> int:
    """
    Calculate maximum number of rows in hexagonal arrangement.
    
    Inverse of stack height formula.
    """
    if pipe_diameter_mm <= 0:
        return 0
    
    # First row is full diameter
    if available_height_mm < pipe_diameter_mm:
        return 0
    
    # Additional rows add D × (√3/2) each
    remaining = available_height_mm - pipe_diameter_mm
    row_increment = pipe_diameter_mm * (math.sqrt(3) / 2)
    
    additional_rows = int(remaining / row_increment)
    return 1 + additional_rows


def calculate_pipes_per_row(
    pipe_diameter_mm: float,
    available_width_mm: float,
    is_offset_row: bool = False
) -> int:
    """
    Calculate how many pipes fit in a row.
    
    For offset rows (hexagonal), pipes are shifted by D/2.
    """
    if pipe_diameter_mm <= 0:
        return 0
    
    if is_offset_row:
        # Offset row starts half diameter in
        effective_width = available_width_mm - (pipe_diameter_mm / 2)
    else:
        effective_width = available_width_mm
    
    return int(effective_width / pipe_diameter_mm)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180.0 / math.pi
