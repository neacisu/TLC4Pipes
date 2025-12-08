"""
Transport Compliance Validator

Validates loading plans against Romanian transport regulations.
Based on OG 43/1997 and CNAIR norms.
"""

from dataclasses import dataclass
from typing import List

# Romanian transport limits
MAX_TOTAL_WEIGHT_KG = 24000      # Max cargo weight
MAX_AXLE_WEIGHT_MOTOR_KG = 11500  # Max tractor motor axle
MAX_AXLE_WEIGHT_TRAILER_KG = 8000  # Max per trailer axle (3 axles)
MAX_VEHICLE_WEIGHT_KG = 40000     # Total vehicle + cargo


@dataclass
class ComplianceResult:
    """Result of transport compliance check."""
    is_compliant: bool
    weight_check: dict
    axle_check: dict
    warnings: List[str]
    violations: List[str]


def check_weight_compliance(
    cargo_weight_kg: float,
    max_payload_kg: float = MAX_TOTAL_WEIGHT_KG
) -> dict:
    """
    Check if cargo weight is within limits.
    
    Args:
        cargo_weight_kg: Total cargo weight
        max_payload_kg: Maximum allowed payload
        
    Returns:
        Dict with compliance status
    """
    is_valid = cargo_weight_kg <= max_payload_kg
    
    return {
        "is_valid": is_valid,
        "cargo_weight_kg": cargo_weight_kg,
        "max_allowed_kg": max_payload_kg,
        "utilization_pct": round((cargo_weight_kg / max_payload_kg) * 100, 1),
        "remaining_kg": max(0, max_payload_kg - cargo_weight_kg),
        "overweight_kg": max(0, cargo_weight_kg - max_payload_kg)
    }


def check_axle_distribution(
    cargo_weight_kg: float,
    center_of_gravity_m: float,
    trailer_length_m: float = 13.6,
    kingpin_position_m: float = 1.5
) -> dict:
    """
    Check axle weight distribution compliance.
    
    Simplified calculation assuming:
    - Kingpin at 1.5m from front of trailer
    - Trailer axle group at rear (average 11m from front)
    
    Args:
        cargo_weight_kg: Total cargo weight
        center_of_gravity_m: CoG distance from front of trailer
        trailer_length_m: Trailer length
        kingpin_position_m: Kingpin distance from front
        
    Returns:
        Dict with axle weight distribution
    """
    # Axle positions (from front of trailer)
    axle_group_position_m = trailer_length_m - 1.5  # ~1.5m from rear
    
    # Lever arm calculations
    cog_to_kingpin = center_of_gravity_m - kingpin_position_m
    cog_to_axle = axle_group_position_m - center_of_gravity_m
    
    # Weight distribution (moment balance)
    total_lever = axle_group_position_m - kingpin_position_m
    
    if total_lever > 0:
        weight_on_axle = (cargo_weight_kg * cog_to_kingpin) / total_lever
        weight_on_kingpin = cargo_weight_kg - weight_on_axle
    else:
        weight_on_axle = cargo_weight_kg / 2
        weight_on_kingpin = cargo_weight_kg / 2
    
    # Check limits
    kingpin_valid = weight_on_kingpin <= MAX_AXLE_WEIGHT_MOTOR_KG
    axle_valid = weight_on_axle <= (MAX_AXLE_WEIGHT_TRAILER_KG * 3)  # Triple axle
    
    return {
        "is_valid": kingpin_valid and axle_valid,
        "kingpin_weight_kg": round(weight_on_kingpin, 0),
        "kingpin_max_kg": MAX_AXLE_WEIGHT_MOTOR_KG,
        "kingpin_valid": kingpin_valid,
        "axle_group_weight_kg": round(weight_on_axle, 0),
        "axle_group_max_kg": MAX_AXLE_WEIGHT_TRAILER_KG * 3,
        "axle_valid": axle_valid,
        "center_of_gravity_m": center_of_gravity_m,
        "optimal_cog_range_m": (5.5, 7.5)  # Optimal CoG range
    }


def validate_transport_compliance(
    cargo_weight_kg: float,
    center_of_gravity_m: float = 6.5,
    trailer_length_m: float = 13.6,
    max_payload_kg: float = MAX_TOTAL_WEIGHT_KG
) -> ComplianceResult:
    """
    Complete transport compliance validation.
    
    Args:
        cargo_weight_kg: Total cargo weight
        center_of_gravity_m: CoG from front of trailer
        trailer_length_m: Trailer length
        max_payload_kg: Maximum payload
        
    Returns:
        ComplianceResult
    """
    warnings = []
    violations = []
    
    # Weight check
    weight_check = check_weight_compliance(cargo_weight_kg, max_payload_kg)
    if not weight_check["is_valid"]:
        violations.append(
            f"Overweight: {weight_check['overweight_kg']:.0f} kg over limit"
        )
    
    # Axle distribution check
    axle_check = check_axle_distribution(
        cargo_weight_kg,
        center_of_gravity_m,
        trailer_length_m
    )
    
    if not axle_check["kingpin_valid"]:
        violations.append(
            f"Kingpin overload: {axle_check['kingpin_weight_kg']:.0f} kg > "
            f"{axle_check['kingpin_max_kg']} kg limit"
        )
    
    if not axle_check["axle_valid"]:
        violations.append(
            f"Axle group overload: {axle_check['axle_group_weight_kg']:.0f} kg > "
            f"{axle_check['axle_group_max_kg']} kg limit"
        )
    
    # CoG warnings
    optimal_min, optimal_max = axle_check["optimal_cog_range_m"]
    if center_of_gravity_m < optimal_min:
        warnings.append(
            f"Center of gravity too far forward ({center_of_gravity_m:.1f}m). "
            f"Optimal range: {optimal_min}-{optimal_max}m"
        )
    elif center_of_gravity_m > optimal_max:
        warnings.append(
            f"Center of gravity too far back ({center_of_gravity_m:.1f}m). "
            f"Optimal range: {optimal_min}-{optimal_max}m"
        )
    
    # High utilization warning
    if weight_check["utilization_pct"] > 95:
        warnings.append(
            f"High weight utilization ({weight_check['utilization_pct']:.1f}%). "
            "Consider safety margin."
        )
    
    is_compliant = weight_check["is_valid"] and axle_check["is_valid"]
    
    return ComplianceResult(
        is_compliant=is_compliant,
        weight_check=weight_check,
        axle_check=axle_check,
        warnings=warnings,
        violations=violations
    )
