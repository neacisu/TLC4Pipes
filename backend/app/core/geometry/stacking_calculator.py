"""
Stacking Calculator

Calculates pipe stacking dimensions and stability.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

from app.utils.constants import (
    STANDARD_TRUCK_HEIGHT_MM,
    MEGA_TRUCK_HEIGHT_MM,
    STANDARD_TRUCK_WIDTH_MM,
)


@dataclass
class StackDimensions:
    """Dimensions of a pipe stack."""
    width_mm: float
    height_mm: float
    length_mm: float
    num_rows: int
    pipes_per_row: int
    total_pipes: int
    volume_m3: float


@dataclass
class StackAnalysis:
    """Complete analysis of pipe stacking."""
    dimensions: StackDimensions
    total_weight_kg: float
    weight_per_row_kg: float
    bottom_row_load_kg: float
    is_stable: bool
    stability_warnings: List[str]


def calculate_square_stack_height(
    diameter_mm: float,
    num_rows: int
) -> float:
    """
    Calculate height of square (non-staggered) stack.
    
    Formula: H = n × D
    """
    return diameter_mm * num_rows


def calculate_hexagonal_stack_height(
    diameter_mm: float,
    num_rows: int
) -> float:
    """
    Calculate height of hexagonal (staggered) stack.
    
    Formula: H = D + (n-1) × D × (√3/2)
    """
    if num_rows <= 1:
        return diameter_mm * num_rows
    
    return diameter_mm + (num_rows - 1) * diameter_mm * (math.sqrt(3) / 2)


def calculate_max_stack_rows(
    diameter_mm: float,
    available_height_mm: float,
    use_hexagonal: bool = True
) -> int:
    """
    Calculate maximum number of rows in available height.
    
    Args:
        diameter_mm: Pipe outer diameter
        available_height_mm: Available vertical space
        use_hexagonal: Use hexagonal (staggered) arrangement
        
    Returns:
        Maximum number of rows
    """
    if diameter_mm <= 0 or available_height_mm < diameter_mm:
        return 0
    
    if use_hexagonal:
        # First row = D, each additional = D × (√3/2)
        remaining = available_height_mm - diameter_mm
        row_height = diameter_mm * (math.sqrt(3) / 2)
        return 1 + int(remaining / row_height)
    else:
        # Square stacking: each row = D
        return int(available_height_mm / diameter_mm)


def calculate_stack_dimensions(
    diameter_mm: float,
    container_width_mm: float = STANDARD_TRUCK_WIDTH_MM,
    container_height_mm: float = STANDARD_TRUCK_HEIGHT_MM,
    pipe_length_mm: float = 12000,
    use_hexagonal: bool = True
) -> StackDimensions:
    """
    Calculate pipe stack dimensions for a container.
    
    Args:
        diameter_mm: Pipe outer diameter
        container_width_mm: Container width
        container_height_mm: Container height
        pipe_length_mm: Pipe length
        use_hexagonal: Use hexagonal arrangement
        
    Returns:
        StackDimensions with counts and volumes
    """
    # Calculate pipes per row (bottom row)
    pipes_per_row = int(container_width_mm / diameter_mm)
    
    # Calculate max rows
    num_rows = calculate_max_stack_rows(
        diameter_mm, container_height_mm, use_hexagonal
    )
    
    # Calculate actual dimensions
    width = pipes_per_row * diameter_mm
    if use_hexagonal:
        height = calculate_hexagonal_stack_height(diameter_mm, num_rows)
    else:
        height = calculate_square_stack_height(diameter_mm, num_rows)
    
    # Total pipes (hexagonal alternates row counts)
    if use_hexagonal:
        total = 0
        for row in range(num_rows):
            if row % 2 == 0:
                total += pipes_per_row
            else:
                total += max(0, pipes_per_row - 1)
    else:
        total = pipes_per_row * num_rows
    
    # Volume in m³
    volume = (width * height * pipe_length_mm) / 1e9
    
    return StackDimensions(
        width_mm=width,
        height_mm=height,
        length_mm=pipe_length_mm,
        num_rows=num_rows,
        pipes_per_row=pipes_per_row,
        total_pipes=total,
        volume_m3=volume
    )


def analyze_stack_stability(
    diameter_mm: float,
    weight_per_meter: float,
    pipe_length_m: float,
    num_rows: int,
    sdr: int
) -> StackAnalysis:
    """
    Analyze stability of a pipe stack.
    
    Args:
        diameter_mm: Pipe outer diameter
        weight_per_meter: Pipe weight per meter
        pipe_length_m: Pipe length in meters
        num_rows: Number of stacking rows
        sdr: Standard Dimension Ratio
        
    Returns:
        StackAnalysis with stability assessment
    """
    warnings = []
    
    # Calculate weights
    single_pipe_weight = weight_per_meter * pipe_length_m
    pipes_per_row = int(STANDARD_TRUCK_WIDTH_MM / diameter_mm)
    
    # Estimate total weight
    total_pipes = 0
    for row in range(num_rows):
        if row % 2 == 0:
            total_pipes += pipes_per_row
        else:
            total_pipes += max(0, pipes_per_row - 1)
    
    total_weight = total_pipes * single_pipe_weight
    weight_per_row = single_pipe_weight * pipes_per_row
    
    # Bottom row bears weight of all pipes above
    bottom_row_load = total_weight - weight_per_row
    
    # Check stability based on SDR
    # Lower SDR = thicker walls = more stable
    max_safe_rows = {
        11: 8,   # PN16
        17: 6,   # PN10
        21: 5,   # PN8
        26: 4,   # PN6
    }.get(sdr, 4)
    
    # Large diameter adjustment
    if diameter_mm >= 500:
        max_safe_rows = min(max_safe_rows, 3)
        warnings.append(
            f"Large diameter (DN{int(diameter_mm)}) limits safe stacking height"
        )
    elif diameter_mm >= 315:
        max_safe_rows = min(max_safe_rows, max_safe_rows - 1)
    
    is_stable = num_rows <= max_safe_rows
    
    if not is_stable:
        warnings.append(
            f"Stacking {num_rows} rows exceeds recommended {max_safe_rows} "
            f"rows for SDR{sdr}"
        )
    
    # Check total load on bottom pipes
    bottom_pipe_load = bottom_row_load / pipes_per_row
    if bottom_pipe_load > 500:  # kg per pipe threshold
        warnings.append(
            f"High load on bottom pipes: {bottom_pipe_load:.0f} kg/pipe"
        )
    
    # Calculate dimensions
    dimensions = StackDimensions(
        width_mm=pipes_per_row * diameter_mm,
        height_mm=calculate_hexagonal_stack_height(diameter_mm, num_rows),
        length_mm=pipe_length_m * 1000,
        num_rows=num_rows,
        pipes_per_row=pipes_per_row,
        total_pipes=total_pipes,
        volume_m3=(pipes_per_row * diameter_mm * calculate_hexagonal_stack_height(
            diameter_mm, num_rows
        ) * pipe_length_m * 1000) / 1e9
    )
    
    return StackAnalysis(
        dimensions=dimensions,
        total_weight_kg=total_weight,
        weight_per_row_kg=weight_per_row,
        bottom_row_load_kg=bottom_row_load,
        is_stable=is_stable,
        stability_warnings=warnings
    )


def calculate_optimal_stacking(
    pipes: List[dict],
    container_width_mm: float = STANDARD_TRUCK_WIDTH_MM,
    container_height_mm: float = STANDARD_TRUCK_HEIGHT_MM
) -> dict:
    """
    Calculate optimal stacking arrangement for mixed pipe diameters.
    
    Strategy: Place largest pipes on bottom for stability.
    
    Args:
        pipes: List of pipe dicts with diameter_mm, quantity, weight_per_meter
        container_width_mm: Container width
        container_height_mm: Container height
        
    Returns:
        Dict with stacking plan
    """
    # Sort by diameter descending (largest on bottom)
    sorted_pipes = sorted(
        pipes, 
        key=lambda p: p.get('dn_mm', 0), 
        reverse=True
    )
    
    layers = []
    current_height = 0
    total_pipes_placed = 0
    
    for pipe_group in sorted_pipes:
        diameter = pipe_group.get('dn_mm', 100)
        quantity = pipe_group.get('quantity', 0)
        
        # How many fit in a row
        per_row = int(container_width_mm / diameter)
        if per_row == 0:
            continue
        
        # How many rows needed
        rows_needed = math.ceil(quantity / per_row)
        
        # Check if rows fit in remaining height
        row_height = diameter * (math.sqrt(3) / 2)
        first_row_height = diameter
        
        for row_idx in range(rows_needed):
            if row_idx == 0:
                height_needed = first_row_height
            else:
                height_needed = row_height
            
            if current_height + height_needed > container_height_mm:
                break
            
            pipes_in_row = min(per_row, quantity - total_pipes_placed)
            layers.append({
                'diameter_mm': diameter,
                'pipes_count': pipes_in_row,
                'row_index': row_idx,
                'y_position_mm': current_height + diameter / 2
            })
            
            current_height += height_needed if row_idx > 0 else first_row_height
            total_pipes_placed += pipes_in_row
    
    return {
        'layers': layers,
        'total_height_mm': current_height,
        'total_pipes_placed': total_pipes_placed,
        'height_utilization': current_height / container_height_mm if container_height_mm > 0 else 0
    }
