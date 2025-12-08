"""
Axle Distribution Calculator

Enhanced axle weight distribution calculations for transport compliance.
Based on Romanian regulations (OG 43/1997, CNAIR norms).
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from app.utils.constants import (
    MAX_AXLE_WEIGHT_MOTOR_KG,
    MAX_AXLE_WEIGHT_TRAILER_KG,
    KINGPIN_POSITION_M,
    OPTIMAL_COG_MIN_M,
    OPTIMAL_COG_MAX_M,
)


@dataclass
class AxleConfig:
    """Configuration for axle calculations."""
    kingpin_position_m: float = KINGPIN_POSITION_M  # From trailer front
    trailer_length_m: float = 13.6
    axle_group_position_m: float = 12.1  # Default: 1.5m from rear
    num_trailer_axles: int = 3
    max_kingpin_load_kg: float = MAX_AXLE_WEIGHT_MOTOR_KG
    max_per_axle_load_kg: float = MAX_AXLE_WEIGHT_TRAILER_KG


@dataclass 
class AxleDistribution:
    """Calculated axle weight distribution."""
    kingpin_load_kg: float
    axle_group_load_kg: float
    per_axle_load_kg: float
    kingpin_utilization_pct: float
    axle_utilization_pct: float
    is_valid: bool
    violation_message: Optional[str]


@dataclass
class DistributionAnalysis:
    """Complete axle distribution analysis."""
    distribution: AxleDistribution
    center_of_gravity_m: float
    cog_from_kingpin_m: float
    is_cog_optimal: bool
    optimization_suggestion: Optional[str]
    warnings: List[str]


def calculate_axle_distribution(
    total_cargo_weight_kg: float,
    center_of_gravity_m: float,
    config: Optional[AxleConfig] = None
) -> AxleDistribution:
    """
    Calculate weight distribution between kingpin and trailer axles.
    
    Uses lever arm principle (moment balance):
    W_axle × (axle_pos - kingpin_pos) = W_total × (CoG - kingpin_pos)
    
    Args:
        total_cargo_weight_kg: Total cargo weight
        center_of_gravity_m: CoG distance from trailer front
        config: Axle configuration (uses defaults if None)
        
    Returns:
        AxleDistribution with load calculations
    """
    if config is None:
        config = AxleConfig()
    
    # Calculate lever arms
    cog_to_kingpin = center_of_gravity_m - config.kingpin_position_m
    axle_to_kingpin = config.axle_group_position_m - config.kingpin_position_m
    
    if axle_to_kingpin <= 0:
        return AxleDistribution(
            kingpin_load_kg=total_cargo_weight_kg,
            axle_group_load_kg=0,
            per_axle_load_kg=0,
            kingpin_utilization_pct=100,
            axle_utilization_pct=0,
            is_valid=False,
            violation_message="Invalid axle configuration"
        )
    
    # Calculate loads using moment balance
    axle_group_load = (total_cargo_weight_kg * cog_to_kingpin) / axle_to_kingpin
    kingpin_load = total_cargo_weight_kg - axle_group_load
    per_axle_load = axle_group_load / config.num_trailer_axles
    
    # Calculate utilizations
    kingpin_util = (kingpin_load / config.max_kingpin_load_kg) * 100
    max_axle_group = config.max_per_axle_load_kg * config.num_trailer_axles
    axle_util = (axle_group_load / max_axle_group) * 100
    
    # Check validity
    violations = []
    if kingpin_load > config.max_kingpin_load_kg:
        excess = kingpin_load - config.max_kingpin_load_kg
        violations.append(f"Kingpin overload by {excess:.0f} kg")
    
    if axle_group_load > max_axle_group:
        excess = axle_group_load - max_axle_group
        violations.append(f"Axle group overload by {excess:.0f} kg")
    
    if per_axle_load > config.max_per_axle_load_kg:
        excess = per_axle_load - config.max_per_axle_load_kg
        violations.append(f"Per-axle overload by {excess:.0f} kg")
    
    is_valid = len(violations) == 0
    violation_msg = "; ".join(violations) if violations else None
    
    return AxleDistribution(
        kingpin_load_kg=round(kingpin_load, 0),
        axle_group_load_kg=round(axle_group_load, 0),
        per_axle_load_kg=round(per_axle_load, 0),
        kingpin_utilization_pct=round(kingpin_util, 1),
        axle_utilization_pct=round(axle_util, 1),
        is_valid=is_valid,
        violation_message=violation_msg
    )


def analyze_distribution(
    total_cargo_weight_kg: float,
    center_of_gravity_m: float,
    config: Optional[AxleConfig] = None
) -> DistributionAnalysis:
    """
    Complete analysis of axle distribution with recommendations.
    
    Args:
        total_cargo_weight_kg: Total cargo weight
        center_of_gravity_m: CoG from trailer front
        config: Axle configuration
        
    Returns:
        DistributionAnalysis with full assessment
    """
    if config is None:
        config = AxleConfig()
    
    distribution = calculate_axle_distribution(
        total_cargo_weight_kg, center_of_gravity_m, config
    )
    
    warnings = []
    suggestion = None
    
    # Check CoG position
    is_cog_optimal = OPTIMAL_COG_MIN_M <= center_of_gravity_m <= OPTIMAL_COG_MAX_M
    cog_from_kingpin = center_of_gravity_m - config.kingpin_position_m
    
    if not is_cog_optimal:
        if center_of_gravity_m < OPTIMAL_COG_MIN_M:
            suggestion = (
                f"Move heavy items back by {OPTIMAL_COG_MIN_M - center_of_gravity_m:.1f}m "
                f"to reach optimal CoG range ({OPTIMAL_COG_MIN_M}-{OPTIMAL_COG_MAX_M}m)"
            )
        else:
            suggestion = (
                f"Move heavy items forward by {center_of_gravity_m - OPTIMAL_COG_MAX_M:.1f}m "
                f"to reach optimal CoG range ({OPTIMAL_COG_MIN_M}-{OPTIMAL_COG_MAX_M}m)"
            )
    
    # Generate warnings
    if distribution.kingpin_utilization_pct > 90:
        warnings.append(
            f"High kingpin load ({distribution.kingpin_utilization_pct:.0f}% of limit)"
        )
    
    if distribution.axle_utilization_pct > 90:
        warnings.append(
            f"High axle load ({distribution.axle_utilization_pct:.0f}% of limit)"
        )
    
    if not distribution.is_valid:
        warnings.append(f"VIOLATION: {distribution.violation_message}")
    
    return DistributionAnalysis(
        distribution=distribution,
        center_of_gravity_m=round(center_of_gravity_m, 2),
        cog_from_kingpin_m=round(cog_from_kingpin, 2),
        is_cog_optimal=is_cog_optimal,
        optimization_suggestion=suggestion,
        warnings=warnings
    )


def calculate_optimal_cog_range(
    total_cargo_weight_kg: float,
    config: Optional[AxleConfig] = None
) -> Tuple[float, float]:
    """
    Calculate the acceptable CoG range for a given weight.
    
    The range depends on the weight - heavier loads have narrower ranges.
    
    Args:
        total_cargo_weight_kg: Total cargo weight
        config: Axle configuration
        
    Returns:
        Tuple of (min_cog_m, max_cog_m) from trailer front
    """
    if config is None:
        config = AxleConfig()
    
    # Calculate min CoG (maximum kingpin load case)
    # W_kingpin_max × axle_to_kingpin = W × (cog - kingpin)
    # cog = kingpin + (W_kingpin_max × axle_to_kingpin) / W
    axle_to_kingpin = config.axle_group_position_m - config.kingpin_position_m
    
    if total_cargo_weight_kg <= 0:
        return (OPTIMAL_COG_MIN_M, OPTIMAL_COG_MAX_M)
    
    # Min CoG: when kingpin is at max
    min_cog = config.kingpin_position_m + (
        (total_cargo_weight_kg - config.max_kingpin_load_kg) * axle_to_kingpin
    ) / total_cargo_weight_kg
    
    # Max CoG: when axle group is at max
    max_axle_group = config.max_per_axle_load_kg * config.num_trailer_axles
    max_cog = config.kingpin_position_m + (
        max_axle_group * axle_to_kingpin
    ) / total_cargo_weight_kg
    
    # Clamp to reasonable trailer range
    min_cog = max(0.5, min_cog)
    max_cog = min(config.trailer_length_m - 0.5, max_cog)
    
    return (round(min_cog, 2), round(max_cog, 2))


def suggest_load_arrangement(
    bundles: List[dict],
    trailer_length_m: float = 13.6,
    target_cog_m: Optional[float] = None
) -> List[dict]:
    """
    Suggest optimal positions for bundles to achieve balanced distribution.
    
    Strategy:
    1. Place heaviest items near target CoG
    2. Balance lighter items on both sides
    
    Args:
        bundles: List of bundle dicts with weight_kg
        trailer_length_m: Trailer length
        target_cog_m: Target CoG position
        
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
    
    result = []
    n = len(sorted_bundles)
    
    # Calculate available loading zone (1m from each end)
    load_start = 1.0
    load_end = trailer_length_m - 1.0
    load_length = load_end - load_start
    
    for i, bundle in enumerate(sorted_bundles):
        bundle_copy = dict(bundle)
        
        if i == 0:
            # Heaviest at target CoG
            pos = target_cog_m
        elif i % 2 == 1:
            # Odd indices: front of target
            offset = ((i + 1) // 2) * (load_length / (n + 1))
            pos = max(load_start, target_cog_m - offset)
        else:
            # Even indices: back of target
            offset = (i // 2) * (load_length / (n + 1))
            pos = min(load_end, target_cog_m + offset)
        
        bundle_copy['suggested_position_m'] = round(pos, 2)
        result.append(bundle_copy)
    
    return result


def calculate_weight_per_axle(
    distribution: AxleDistribution,
    num_axles: int = 3
) -> dict:
    """
    Calculate load per individual trailer axle.
    
    Assumes equal distribution among trailer axles.
    
    Args:
        distribution: Calculated distribution
        num_axles: Number of trailer axles
        
    Returns:
        Dict with per-axle breakdown
    """
    per_axle = distribution.axle_group_load_kg / num_axles if num_axles > 0 else 0
    
    return {
        'kingpin_kg': distribution.kingpin_load_kg,
        'trailer_axle_1_kg': round(per_axle, 0),
        'trailer_axle_2_kg': round(per_axle, 0),
        'trailer_axle_3_kg': round(per_axle, 0) if num_axles >= 3 else 0,
        'total_kg': round(
            distribution.kingpin_load_kg + distribution.axle_group_load_kg, 0
        )
    }
