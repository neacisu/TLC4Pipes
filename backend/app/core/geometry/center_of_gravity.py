"""
Center of Gravity Calculator

Calculates load center of gravity for axle weight distribution.
Based on specification section 7.1 - Romanian transport regulations.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

from app.utils.constants import (
    OPTIMAL_COG_MIN_M,
    OPTIMAL_COG_MAX_M,
    KINGPIN_POSITION_M,
    MAX_AXLE_WEIGHT_MOTOR_KG,
    MAX_AXLE_WEIGHT_TRAILER_KG,
)


@dataclass
class LoadItem:
    """Single load item with position and weight."""
    weight_kg: float
    x_position_m: float  # Distance from front of trailer
    description: Optional[str] = None


@dataclass
class CenterOfGravityResult:
    """Result of center of gravity calculation."""
    cog_x_m: float           # Distance from trailer front
    cog_from_kingpin_m: float
    total_weight_kg: float
    is_optimal: bool
    deviation_from_optimal_m: float
    recommendation: str


@dataclass
class AxleLoadResult:
    """Axle load distribution result."""
    kingpin_load_kg: float       # Load on tractor via kingpin
    axle_group_load_kg: float    # Load on trailer axles
    kingpin_valid: bool
    axle_valid: bool
    total_valid: bool
    messages: List[str]


def calculate_center_of_gravity(
    items: List[LoadItem]
) -> CenterOfGravityResult:
    """
    Calculate center of gravity for loaded items.
    
    Uses weighted average: CoG = Σ(weight × position) / Σ(weight)
    
    Args:
        items: List of load items with position and weight
        
    Returns:
        CenterOfGravityResult
    """
    if not items:
        return CenterOfGravityResult(
            cog_x_m=0,
            cog_from_kingpin_m=0,
            total_weight_kg=0,
            is_optimal=True,
            deviation_from_optimal_m=0,
            recommendation="No load"
        )
    
    total_weight = sum(item.weight_kg for item in items)
    if total_weight == 0:
        return CenterOfGravityResult(
            cog_x_m=0,
            cog_from_kingpin_m=0,
            total_weight_kg=0,
            is_optimal=True,
            deviation_from_optimal_m=0,
            recommendation="Zero weight load"
        )
    
    # Weighted average position
    weighted_sum = sum(item.weight_kg * item.x_position_m for item in items)
    cog_x = weighted_sum / total_weight
    
    # Distance from kingpin
    cog_from_kingpin = cog_x - KINGPIN_POSITION_M
    
    # Check if in optimal range
    optimal_center = (OPTIMAL_COG_MIN_M + OPTIMAL_COG_MAX_M) / 2
    deviation = cog_x - optimal_center
    is_optimal = OPTIMAL_COG_MIN_M <= cog_x <= OPTIMAL_COG_MAX_M
    
    # Generate recommendation
    if is_optimal:
        recommendation = "Center of gravity is in optimal range"
    elif cog_x < OPTIMAL_COG_MIN_M:
        recommendation = (
            f"Load is too far forward ({cog_x:.1f}m). "
            f"Move heavy items back toward axles."
        )
    else:
        recommendation = (
            f"Load is too far back ({cog_x:.1f}m). "
            f"Move heavy items forward toward kingpin."
        )
    
    return CenterOfGravityResult(
        cog_x_m=cog_x,
        cog_from_kingpin_m=cog_from_kingpin,
        total_weight_kg=total_weight,
        is_optimal=is_optimal,
        deviation_from_optimal_m=deviation,
        recommendation=recommendation
    )


def calculate_axle_loads(
    total_weight_kg: float,
    cog_x_m: float,
    trailer_length_m: float = 13.6,
    kingpin_position_m: float = KINGPIN_POSITION_M,
    axle_position_m: Optional[float] = None
) -> AxleLoadResult:
    """
    Calculate load distribution between kingpin and trailer axles.
    
    Uses lever arm calculation (moment balance):
    - Weight on axles × (axle - kingpin) = Total × (CoG - kingpin)
    
    Args:
        total_weight_kg: Total cargo weight
        cog_x_m: Center of gravity from trailer front
        trailer_length_m: Trailer length
        kingpin_position_m: Kingpin distance from front
        axle_position_m: Axle group position (default: 1.5m from rear)
        
    Returns:
        AxleLoadResult with distribution
    """
    if axle_position_m is None:
        axle_position_m = trailer_length_m - 1.5
    
    messages = []
    
    # Lever arm distances
    cog_to_kingpin = cog_x_m - kingpin_position_m
    axle_to_kingpin = axle_position_m - kingpin_position_m
    
    if axle_to_kingpin <= 0:
        # Invalid configuration
        return AxleLoadResult(
            kingpin_load_kg=total_weight_kg,
            axle_group_load_kg=0,
            kingpin_valid=False,
            axle_valid=True,
            total_valid=False,
            messages=["Invalid axle configuration"]
        )
    
    # Moment balance: solve for axle load
    # axle_load × axle_to_kingpin = total × cog_to_kingpin
    axle_load = (total_weight_kg * cog_to_kingpin) / axle_to_kingpin
    kingpin_load = total_weight_kg - axle_load
    
    # Validate against limits
    kingpin_valid = kingpin_load <= MAX_AXLE_WEIGHT_MOTOR_KG
    axle_valid = axle_load <= (MAX_AXLE_WEIGHT_TRAILER_KG * 3)  # Triple axle
    
    if not kingpin_valid:
        overload = kingpin_load - MAX_AXLE_WEIGHT_MOTOR_KG
        messages.append(
            f"Kingpin overload by {overload:.0f} kg. "
            f"Move load back toward axles."
        )
    
    if not axle_valid:
        max_axle = MAX_AXLE_WEIGHT_TRAILER_KG * 3
        overload = axle_load - max_axle
        messages.append(
            f"Axle group overload by {overload:.0f} kg. "
            f"Move load forward toward kingpin."
        )
    
    if kingpin_valid and axle_valid:
        messages.append("Load distribution is within legal limits")
    
    return AxleLoadResult(
        kingpin_load_kg=kingpin_load,
        axle_group_load_kg=axle_load,
        kingpin_valid=kingpin_valid,
        axle_valid=axle_valid,
        total_valid=kingpin_valid and axle_valid,
        messages=messages
    )


def calculate_bundle_cog(
    bundles: List[dict],
    pipe_length_m: float = 12.0
) -> Tuple[float, float, float]:
    """
    Calculate center of gravity for pipe bundles in truck.
    
    Assumes bundles are loaded from front to back evenly.
    
    Args:
        bundles: List of bundle dicts with weight_kg and optional x_position_m
        pipe_length_m: Pipe length (for longitudinal CoG - assumed centered)
        
    Returns:
        Tuple of (cog_x_m, cog_y_m, total_weight_kg)
    """
    if not bundles:
        return 0, 0, 0
    
    total_weight = sum(b.get('weight_kg', 0) for b in bundles)
    if total_weight == 0:
        return 0, 0, 0
    
    # Calculate weighted positions
    # If no position specified, distribute evenly starting from 1m
    items_with_pos = []
    unpositioned = []
    
    for b in bundles:
        if 'x_position_m' in b:
            items_with_pos.append(b)
        else:
            unpositioned.append(b)
    
    # Distribute unpositioned bundles evenly
    if unpositioned:
        # Start at 1m, space evenly with 0.5m gaps
        start_pos = 1.0
        spacing = 0.5
        for i, b in enumerate(unpositioned):
            b['x_position_m'] = start_pos + i * spacing
    
    # Calculate weighted average
    weighted_x = sum(
        b.get('weight_kg', 0) * b.get('x_position_m', 6.0) 
        for b in bundles
    )
    
    # Assume y (height) CoG at geometric center of bundles
    # Simplified - would need actual stacking positions
    weighted_y = sum(
        b.get('weight_kg', 0) * b.get('y_position_m', 1.0)
        for b in bundles
    )
    
    cog_x = weighted_x / total_weight
    cog_y = weighted_y / total_weight
    
    return cog_x, cog_y, total_weight


def optimize_load_positions(
    bundles: List[dict],
    trailer_length_m: float = 13.6,
    target_cog_m: Optional[float] = None
) -> List[dict]:
    """
    Suggest optimal positions for bundles to achieve target CoG.
    
    Strategy: Place heavy bundles near optimal CoG, 
    lighter bundles at edges.
    
    Args:
        bundles: List of bundle dicts with weight_kg
        trailer_length_m: Trailer length
        target_cog_m: Target CoG (default: center of optimal range)
        
    Returns:
        Bundles with suggested x_position_m
    """
    if not bundles:
        return []
    
    if target_cog_m is None:
        target_cog_m = (OPTIMAL_COG_MIN_M + OPTIMAL_COG_MAX_M) / 2
    
    # Sort by weight descending
    sorted_bundles = sorted(
        bundles,
        key=lambda b: b.get('weight_kg', 0),
        reverse=True
    )
    
    # Assign positions: heavy items near target, light at edges
    n = len(sorted_bundles)
    positions = []
    
    # Create position slots centered around target
    usable_length = trailer_length_m - 2  # Leave 1m margins
    slot_width = usable_length / max(n, 1)
    
    for i, bundle in enumerate(sorted_bundles):
        if i == 0:
            # Heaviest at target
            pos = target_cog_m
        elif i % 2 == 1:
            # Alternate front and back of target
            offset = (i + 1) // 2 * slot_width
            pos = target_cog_m - offset
        else:
            offset = i // 2 * slot_width
            pos = target_cog_m + offset
        
        # Clamp to valid range
        pos = max(1.0, min(trailer_length_m - 1.0, pos))
        
        bundle_copy = dict(bundle)
        bundle_copy['x_position_m'] = pos
        positions.append(bundle_copy)
    
    return positions


def calculate_cog_from_truck_load(
    trucks: List[dict],
    pipe_length_m: float = 12.0
) -> dict:
    """
    Calculate overall CoG from complete truck load.
    
    Args:
        trucks: List of truck load dicts with bundles
        pipe_length_m: Pipe length
        
    Returns:
        Dict with CoG analysis for each truck
    """
    results = []
    
    for i, truck in enumerate(trucks):
        bundles = truck.get('bundles', [])
        
        # Create load items from bundles
        items = []
        for j, bundle in enumerate(bundles):
            weight = bundle.get('bundle_weight_kg', 0)
            # Default position: spread evenly
            position = 1.0 + j * 0.5
            items.append(LoadItem(
                weight_kg=weight,
                x_position_m=position,
                description=bundle.get('outer_pipe', {}).get('code', f'Bundle {j+1}')
            ))
        
        cog_result = calculate_center_of_gravity(items)
        axle_result = calculate_axle_loads(
            cog_result.total_weight_kg,
            cog_result.cog_x_m
        )
        
        results.append({
            'truck_number': i + 1,
            'cog_x_m': round(cog_result.cog_x_m, 2),
            'total_weight_kg': round(cog_result.total_weight_kg, 0),
            'is_cog_optimal': cog_result.is_optimal,
            'kingpin_load_kg': round(axle_result.kingpin_load_kg, 0),
            'axle_load_kg': round(axle_result.axle_group_load_kg, 0),
            'is_axle_valid': axle_result.total_valid,
            'messages': axle_result.messages
        })
    
    return {'trucks': results}
