"""
Gap Clearance Calculator

Calculates minimum clearance required for safe pipe telescoping.
Based on specification document section 3.1.

Formula: Gap_min = C_base + (Factor_diameter × DN_outer)
- C_base = 15mm (minimum for handling and straps)
- Factor_diameter = 0.015 (1.5% for proportional ovality)
"""

from dataclasses import dataclass
from typing import Optional


# Constants from specification document
BASE_CLEARANCE_MM = 15.0  # Minimum absolute gap
DIAMETER_FACTOR = 0.015   # 1.5% of outer diameter
OVALITY_FACTOR = 0.04     # 4% max ovality during transport


@dataclass
class ClearanceResult:
    """Result of gap clearance calculation."""
    available_gap_mm: float
    required_gap_mm: float
    is_valid: bool
    ovality_adjusted_inner_mm: float
    message: str


def calculate_minimum_gap(outer_diameter_mm: float) -> float:
    """
    Calculate minimum required gap for safe nesting.
    
    Args:
        outer_diameter_mm: Outer diameter of the host pipe
        
    Returns:
        Minimum gap in mm required for safe insertion
    """
    return BASE_CLEARANCE_MM + (DIAMETER_FACTOR * outer_diameter_mm)


def calculate_effective_inner_diameter(
    inner_diameter_mm: float,
    outer_diameter_mm: float,
    ovality_factor: float = OVALITY_FACTOR
) -> float:
    """
    Calculate effective inner diameter accounting for ovality.
    
    Ovality can reduce the vertical diameter by 3-4% during storage/transport.
    We use the outer diameter as reference for ovality calculation.
    
    Args:
        inner_diameter_mm: Nominal inner diameter
        outer_diameter_mm: Outer diameter (for ovality reference)
        ovality_factor: Expected ovality (default 4%)
        
    Returns:
        Reduced effective inner diameter
    """
    ovality_reduction = outer_diameter_mm * ovality_factor
    return inner_diameter_mm - ovality_reduction


def validate_nesting_compatibility(
    host_inner_diameter_mm: float,
    host_outer_diameter_mm: float,
    guest_outer_diameter_mm: float,
    apply_ovality: bool = True
) -> ClearanceResult:
    """
    Validate if a guest pipe can be nested inside a host pipe.
    
    Based on specification document examples:
    - TPE315/PN6 (DE=315) in TPE400/PN6 (DI=369.4): Valid (gap=54.4 > 21mm)
    - TPE355/PN6 (DE=355) in TPE400/PN6 (DI=369.4): Invalid (gap=14.4 < 21mm)
    
    Args:
        host_inner_diameter_mm: Inner diameter of host (outer) pipe
        host_outer_diameter_mm: Outer diameter of host pipe (for gap calc)
        guest_outer_diameter_mm: Outer diameter of guest (inner) pipe
        apply_ovality: Whether to account for ovality reduction
        
    Returns:
        ClearanceResult with validation details
    """
    # Calculate effective inner diameter with ovality
    if apply_ovality:
        effective_inner = calculate_effective_inner_diameter(
            host_inner_diameter_mm,
            host_outer_diameter_mm
        )
    else:
        effective_inner = host_inner_diameter_mm
    
    # Calculate available and required gaps
    available_gap = effective_inner - guest_outer_diameter_mm
    required_gap = calculate_minimum_gap(host_outer_diameter_mm)
    
    # Determine validity
    is_valid = available_gap >= required_gap
    
    # Generate message
    if is_valid:
        message = f"Valid: {available_gap:.1f}mm gap >= {required_gap:.1f}mm required"
    else:
        deficit = required_gap - available_gap
        message = f"Invalid: {available_gap:.1f}mm gap < {required_gap:.1f}mm required (deficit: {deficit:.1f}mm)"
    
    return ClearanceResult(
        available_gap_mm=available_gap,
        required_gap_mm=required_gap,
        is_valid=is_valid,
        ovality_adjusted_inner_mm=effective_inner,
        message=message
    )


def find_compatible_pipes(
    host_pipe: dict,
    candidate_pipes: list[dict],
    apply_ovality: bool = True
) -> list[dict]:
    """
    Find all pipes that can be nested inside a host pipe.
    
    Args:
        host_pipe: Dict with inner_diameter_mm and outer_diameter_mm (or dn_mm)
        candidate_pipes: List of pipe dicts with outer_diameter_mm
        apply_ovality: Whether to account for ovality
        
    Returns:
        List of compatible pipe dicts, sorted by outer diameter descending
    """
    host_inner = host_pipe.get("inner_diameter_mm", 0)
    host_outer = host_pipe.get("outer_diameter_mm") or host_pipe.get("dn_mm", 0)
    
    compatible = []
    for candidate in candidate_pipes:
        guest_outer = candidate.get("outer_diameter_mm") or candidate.get("dn_mm", 0)
        
        # Skip if guest is larger than or equal to host
        if guest_outer >= host_outer:
            continue
            
        result = validate_nesting_compatibility(
            host_inner,
            host_outer,
            guest_outer,
            apply_ovality
        )
        
        if result.is_valid:
            compatible.append({
                **candidate,
                "clearance_result": result
            })
    
    # Sort by outer diameter descending (largest compatible first)
    compatible.sort(
        key=lambda p: p.get("outer_diameter_mm") or p.get("dn_mm", 0),
        reverse=True
    )
    
    return compatible
