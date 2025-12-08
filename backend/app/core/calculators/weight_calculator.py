"""
Weight Calculator

Calculates pipe weights for orders and loading plans.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class WeightResult:
    """Result of weight calculation."""
    unit_weight_kg: float       # Weight of single pipe
    total_weight_kg: float      # Total weight for quantity
    weight_per_meter: float     # Weight per meter (from catalog)
    pipe_length_m: float
    quantity: int


def calculate_pipe_weight(
    weight_per_meter: float,
    pipe_length_m: float,
    quantity: int = 1
) -> WeightResult:
    """
    Calculate weight for pipes.
    
    Args:
        weight_per_meter: Weight per meter from catalog (kg/m)
        pipe_length_m: Pipe length (12, 12.5, or 13 meters)
        quantity: Number of pipes
        
    Returns:
        WeightResult with calculated weights
    """
    unit_weight = weight_per_meter * pipe_length_m
    total_weight = unit_weight * quantity
    
    return WeightResult(
        unit_weight_kg=unit_weight,
        total_weight_kg=total_weight,
        weight_per_meter=weight_per_meter,
        pipe_length_m=pipe_length_m,
        quantity=quantity
    )


def calculate_order_total_weight(
    order_items: list[dict],
    pipe_length_m: float = 12.0
) -> float:
    """
    Calculate total weight for all order items.
    
    Args:
        order_items: List of dicts with 'weight_per_meter' and 'quantity'
        pipe_length_m: Pipe length for all items
        
    Returns:
        Total weight in kg
    """
    total = 0.0
    for item in order_items:
        weight_per_m = item.get("weight_per_meter", 0)
        qty = item.get("quantity", 0)
        total += weight_per_m * pipe_length_m * qty
    return total


def calculate_bundle_weight(
    pipes: list[dict],
    pipe_length_m: float = 12.0
) -> float:
    """
    Calculate total weight of a nested bundle.
    
    Args:
        pipes: List of pipe dicts in the bundle (with weight_per_meter)
        pipe_length_m: Pipe length
        
    Returns:
        Total bundle weight in kg
    """
    return sum(
        pipe.get("weight_per_meter", 0) * pipe_length_m
        for pipe in pipes
    )


def check_weight_limits(
    total_weight_kg: float,
    max_payload_kg: float = 24000,
    max_axle_weight_kg: float = 11500
) -> dict:
    """
    Check if weight is within legal limits.
    
    Args:
        total_weight_kg: Total cargo weight
        max_payload_kg: Maximum truck payload (default 24t)
        max_axle_weight_kg: Maximum axle weight (default 11.5t)
        
    Returns:
        Dict with validation results
    """
    is_valid = total_weight_kg <= max_payload_kg
    utilization_pct = (total_weight_kg / max_payload_kg) * 100
    remaining_kg = max_payload_kg - total_weight_kg
    
    return {
        "is_valid": is_valid,
        "total_weight_kg": total_weight_kg,
        "max_payload_kg": max_payload_kg,
        "utilization_pct": round(utilization_pct, 1),
        "remaining_kg": max(0, remaining_kg),
        "overweight_kg": max(0, total_weight_kg - max_payload_kg)
    }


# Heavy extraction warning threshold from specification
HEAVY_EXTRACTION_THRESHOLD_KG = 2000


def check_extraction_requirements(bundle_weight_kg: float) -> dict:
    """
    Check if bundle requires heavy equipment for extraction.
    
    From specification section 3.2:
    If nested bundle weight > 2000 kg, warn user.
    
    Args:
        bundle_weight_kg: Total weight of nested bundle
        
    Returns:
        Dict with extraction assessment
    """
    requires_heavy_equipment = bundle_weight_kg > HEAVY_EXTRACTION_THRESHOLD_KG
    
    return {
        "bundle_weight_kg": bundle_weight_kg,
        "requires_heavy_equipment": requires_heavy_equipment,
        "threshold_kg": HEAVY_EXTRACTION_THRESHOLD_KG,
        "message": (
            "Requires heavy equipment for extraction"
            if requires_heavy_equipment
            else "Standard extraction possible"
        )
    }
