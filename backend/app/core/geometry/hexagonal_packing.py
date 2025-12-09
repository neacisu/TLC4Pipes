"""
Hexagonal Packing Calculator

Calculates optimal hexagonal (staggered) arrangement of pipes.
From specification section 4.2: ~90% density vs 78.5% for square packing.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class PipePosition:
    """Position of a pipe in the cross-section."""
    x_mm: float  # Horizontal center position
    y_mm: float  # Vertical center position
    diameter_mm: float
    row: int
    column: int
    is_offset_row: bool


@dataclass
class PackingResult:
    """Result of hexagonal packing calculation."""
    positions: List[PipePosition]
    total_pipes: int
    rows: int
    max_per_row: int
    stack_width_mm: float
    stack_height_mm: float
    packing_efficiency: float


# Hexagonal packing constants
SQRT3_OVER_2 = math.sqrt(3) / 2  # ≈ 0.866


def calculate_row_height_mm(diameter_mm: float) -> float:
    """
    Calculate vertical distance between row centers in hexagonal packing.
    
    In hexagonal packing, rows are offset by D/2 horizontally,
    and the vertical distance is D × (√3/2).
    """
    return diameter_mm * SQRT3_OVER_2


def calculate_stack_height_mm(
    diameter_mm: float,
    num_rows: int
) -> float:
    """
    Calculate total height of hexagonal stack.
    
    Formula: H = D + (n-1) × D × (√3/2)
    
    Args:
        diameter_mm: Pipe outer diameter
        num_rows: Number of rows in stack
        
    Returns:
        Total height of stack in mm
    """
    if num_rows <= 0:
        return 0.0
    if num_rows == 1:
        return diameter_mm
    
    row_increment = calculate_row_height_mm(diameter_mm)
    return diameter_mm + (num_rows - 1) * row_increment


def calculate_max_rows(
    diameter_mm: float,
    available_height_mm: float
) -> int:
    """
    Calculate maximum number of rows that fit in available height.
    
    Args:
        diameter_mm: Pipe outer diameter
        available_height_mm: Available vertical space (truck height)
        
    Returns:
        Maximum number of rows
    """
    if diameter_mm <= 0 or available_height_mm < diameter_mm:
        return 0
    
    # First row takes full diameter
    remaining = available_height_mm - diameter_mm
    
    # Additional rows take D × (√3/2) each
    row_increment = calculate_row_height_mm(diameter_mm)
    additional_rows = int(remaining / row_increment)
    
    return 1 + additional_rows


def calculate_pipes_per_row(
    diameter_mm: float,
    available_width_mm: float,
    is_offset_row: bool = False
) -> int:
    """
    Calculate how many pipes fit in a row.
    
    Args:
        diameter_mm: Pipe outer diameter
        available_width_mm: Available horizontal space (truck width)
        is_offset_row: Whether this is an offset row (shifted by D/2)
        
    Returns:
        Number of pipes that fit
    """
    if diameter_mm <= 0:
        return 0
    
    if is_offset_row:
        # Offset rows start half-diameter in from both sides
        effective_width = available_width_mm - diameter_mm
    else:
        effective_width = available_width_mm
    
    return max(0, int(effective_width / diameter_mm))


def calculate_hexagonal_packing(
    diameter_mm: float,
    container_width_mm: float,
    container_height_mm: float,
    start_offset: bool = False
) -> PackingResult:
    """
    Calculate hexagonal packing of uniform pipes in a rectangular container.
    
    Args:
        diameter_mm: Pipe outer diameter
        container_width_mm: Container width (truck internal width)
        container_height_mm: Container height (truck internal height)
        start_offset: Whether first row should be offset
        
    Returns:
        PackingResult with all pipe positions
    """
    if diameter_mm <= 0:
        return PackingResult(
            positions=[], total_pipes=0, rows=0, max_per_row=0,
            stack_width_mm=0, stack_height_mm=0, packing_efficiency=0
        )
    
    positions: List[PipePosition] = []
    row_increment = calculate_row_height_mm(diameter_mm)
    
    # Calculate row positions
    row = 0
    current_y = diameter_mm / 2  # Center of first row
    
    while current_y + diameter_mm / 2 <= container_height_mm:
        is_offset = (row % 2 == 1) if not start_offset else (row % 2 == 0)
        pipes_in_row = calculate_pipes_per_row(diameter_mm, container_width_mm, is_offset)
        
        if pipes_in_row == 0:
            break
        
        # Calculate x positions for this row
        if is_offset:
            start_x = diameter_mm  # Start one diameter in
        else:
            start_x = diameter_mm / 2  # Start at half diameter
        
        for col in range(pipes_in_row):
            x = start_x + col * diameter_mm
            positions.append(PipePosition(
                x_mm=x,
                y_mm=current_y,
                diameter_mm=diameter_mm,
                row=row,
                column=col,
                is_offset_row=is_offset
            ))
        
        row += 1
        current_y += row_increment
    
    # Calculate statistics
    total_pipes = len(positions)
    rows = row
    max_per_row = max(
        (sum(1 for p in positions if p.row == r) for r in range(rows)),
        default=0
    )
    
    if positions:
        stack_width = max(p.x_mm + diameter_mm / 2 for p in positions)
        stack_height = max(p.y_mm + diameter_mm / 2 for p in positions)
    else:
        stack_width = 0
        stack_height = 0
    
    # Calculate packing efficiency (area of circles / container area used)
    circle_area = total_pipes * math.pi * (diameter_mm / 2) ** 2
    container_area = stack_width * stack_height if (stack_width and stack_height) else 1
    efficiency = circle_area / container_area if container_area > 0 else 0
    
    return PackingResult(
        positions=positions,
        total_pipes=total_pipes,
        rows=rows,
        max_per_row=max_per_row,
        stack_width_mm=stack_width,
        stack_height_mm=stack_height,
        packing_efficiency=efficiency
    )


def calculate_mixed_diameter_packing(
    large_diameter_mm: float,
    small_diameter_mm: float,
    container_width_mm: float,
    container_height_mm: float
) -> Tuple[int, int, float]:
    """
    Calculate packing with two different pipe diameters.
    
    Places large pipes first, then fills gaps with small pipes.
    Simplified approach - actual implementation would need circle packing.
    
    Args:
        large_diameter_mm: Large pipe diameter
        small_diameter_mm: Small pipe diameter
        container_width_mm: Container width
        container_height_mm: Container height
        
    Returns:
        Tuple of (large_pipe_count, small_pipe_count, efficiency)
    """
    # First, pack large pipes
    large_result = calculate_hexagonal_packing(
        large_diameter_mm,
        container_width_mm,
        container_height_mm
    )
    
    # Estimate remaining space for small pipes
    # This is simplified - real implementation would use circle packing
    occupied_area = large_result.total_pipes * math.pi * (large_diameter_mm / 2) ** 2
    total_area = container_width_mm * container_height_mm
    remaining_area = total_area - occupied_area
    
    # Estimate how many small pipes fit in remaining space (with ~60% efficiency for gaps)
    small_circle_area = math.pi * (small_diameter_mm / 2) ** 2
    estimated_small = int(remaining_area * 0.6 / small_circle_area)
    
    total_occupied = occupied_area + estimated_small * small_circle_area
    efficiency = total_occupied / total_area if total_area > 0 else 0
    
    return large_result.total_pipes, estimated_small, efficiency


def validate_stacking_layers(
    diameter_mm: float,
    weight_per_meter: float,
    num_layers: int,
    sdr: int
) -> Tuple[bool, Optional[str]]:
    """
    Validate if pipes can safely support the stacking load.
    
    Lower SDR (thicker walls) can support more layers.
    
    Args:
        diameter_mm: Pipe outer diameter
        weight_per_meter: Pipe weight per meter
        num_layers: Number of stacking layers
        sdr: Standard Dimension Ratio
        
    Returns:
        Tuple of (is_safe, warning_message)
    """
    # Max layers based on SDR (thicker walls = more layers)
    max_layers_by_sdr = {
        11: 8,   # PN16 - strongest
        17: 6,   # PN10
        21: 5,   # PN8
        26: 4,   # PN6 - weakest
    }
    
    max_allowed = max_layers_by_sdr.get(sdr, 4)
    
    # Larger diameter pipes are more prone to ovalisation
    if diameter_mm >= 500:
        max_allowed = min(max_allowed, 3)
    elif diameter_mm >= 315:
        max_allowed -= 1
    
    if num_layers > max_allowed:
        return False, (
            f"SDR{sdr} pipes with DN{diameter_mm} should not exceed "
            f"{max_allowed} stacking layers (requested {num_layers})"
        )
    
    return True, None


def estimate_mixed_stack_height(
    diameters: List[float],
    container_width_mm: float,
    gap_mm: float = 20.0
) -> float:
    """
    Estimate total height needed to stack bundles with different diameters.
    
    Uses row-based hexagonal packing simulation:
    1. Sort bundles by diameter descending
    2. Place in rows until width is exceeded
    3. Stack rows using hex spacing factor (sqrt(3)/2)
    
    Args:
        diameters: List of bundle outer diameters (mm)
        container_width_mm: Container width (mm)
        gap_mm: Gap between bundles (mm)
        
    Returns:
        Estimated stack height (mm)
    """
    if not diameters:
        return 0.0
    
    # Sort by diameter descending
    sorted_diameters = sorted(diameters, reverse=True)
    
    # Track row heights (use max diameter per row for hex calculation)
    rows: List[float] = []  # Max diameter in each row
    current_z = 0.0
    row_max_diameter = 0.0
    
    for diameter in sorted_diameters:
        # Check if fits in current row
        if current_z + diameter > container_width_mm:
            # Save current row max and start new row
            if row_max_diameter > 0:
                rows.append(row_max_diameter)
            current_z = 0.0
            row_max_diameter = 0.0
        
        current_z += diameter + gap_mm
        row_max_diameter = max(row_max_diameter, diameter)
    
    # Don't forget last row
    if row_max_diameter > 0:
        rows.append(row_max_diameter)
    
    if not rows:
        return 0.0
    
    # Calculate total height using hexagonal stacking
    # First row: full diameter of largest pipe in that row
    total_height = rows[0]
    
    # Subsequent rows: use average diameter for hex spacing
    for i in range(1, len(rows)):
        avg_diameter = (rows[i-1] + rows[i]) / 2
        total_height += avg_diameter * SQRT3_OVER_2
    
    return total_height

