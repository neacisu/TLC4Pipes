"""
Nesting Validator

Validates pipe nesting (telescoping) compatibility with safety rules.
"""

from dataclasses import dataclass
from typing import List, Tuple

from app.core.calculators.gap_clearance import (
    validate_nesting_compatibility,
    ClearanceResult,
)
from app.utils.constants import MAX_NESTING_LEVELS


@dataclass
class NestingValidationResult:
    """Result of complete nesting validation."""
    is_valid: bool
    clearance_check: ClearanceResult
    weight_check: dict
    warnings: List[str]


def validate_single_nesting(
    outer_pipe: dict,
    inner_pipe: dict,
    apply_ovality: bool = True
) -> NestingValidationResult:
    """
    Validate nesting of one pipe inside another.
    
    Checks:
    1. Gap clearance (geometry)
    2. Weight ratio (inner not too heavy for outer)
    3. SDR compatibility (warns if heavy inside light)
    
    Args:
        outer_pipe: Dict with inner_diameter_mm, dn_mm, weight_per_meter, sdr
        inner_pipe: Dict with dn_mm, weight_per_meter, sdr
        
    Returns:
        NestingValidationResult
    """
    warnings = []
    
    # 1. Gap clearance check
    clearance = validate_nesting_compatibility(
        host_inner_diameter_mm=outer_pipe.get("inner_diameter_mm", 0),
        host_outer_diameter_mm=outer_pipe.get("dn_mm", 0),
        guest_outer_diameter_mm=inner_pipe.get("dn_mm", 0),
        apply_ovality=apply_ovality
    )
    
    # 2. Weight ratio check
    outer_weight = outer_pipe.get("weight_per_meter", 0)
    inner_weight = inner_pipe.get("weight_per_meter", 0)
    
    weight_ratio = inner_weight / outer_weight if outer_weight > 0 else 999
    weight_valid = weight_ratio <= 2.0  # Inner should not be more than 2x heavier
    
    weight_check = {
        "is_valid": weight_valid,
        "outer_weight_per_m": outer_weight,
        "inner_weight_per_m": inner_weight,
        "weight_ratio": round(weight_ratio, 2)
    }
    
    if not weight_valid:
        warnings.append(
            f"Inner pipe ({inner_weight:.1f} kg/m) is more than 2x heavier than "
            f"outer pipe ({outer_weight:.1f} kg/m)"
        )
    
    # 3. SDR compatibility warning
    outer_sdr = outer_pipe.get("sdr", 0)
    inner_sdr = inner_pipe.get("sdr", 0)
    
    # Higher SDR = thinner wall = less rigid
    if outer_sdr > inner_sdr and inner_weight > outer_weight:
        warnings.append(
            f"Caution: Heavier pipe (SDR{inner_sdr}) inside lighter pipe (SDR{outer_sdr}) "
            "may cause outer pipe deformation"
        )
    
    return NestingValidationResult(
        is_valid=clearance.is_valid and weight_valid,
        clearance_check=clearance,
        weight_check=weight_check,
        warnings=warnings
    )


def validate_nesting_chain(
    pipes: List[dict],
    max_levels: int = MAX_NESTING_LEVELS
) -> Tuple[bool, List[NestingValidationResult], List[str]]:
    """
    Validate a chain of nested pipes (from outer to inner).
    
    Args:
        pipes: List of pipe dicts, ordered from outer to innermost
        max_levels: Maximum allowed nesting depth
        
    Returns:
        Tuple of (is_valid, list of results, list of warnings)
    """
    if len(pipes) < 2:
        return True, [], []
    
    if len(pipes) > max_levels:
        return False, [], [f"Exceeds max nesting levels ({max_levels})"]
    
    all_warnings = []
    results = []
    all_valid = True
    
    for i in range(len(pipes) - 1):
        outer = pipes[i]
        inner = pipes[i + 1]
        
        result = validate_single_nesting(outer, inner)
        results.append(result)
        
        if not result.is_valid:
            all_valid = False
            all_warnings.append(
                f"Level {i+1}: {outer.get('code')} -> {inner.get('code')} invalid"
            )
        
        all_warnings.extend(result.warnings)
    
    return all_valid, results, all_warnings
