"""
Nesting Algorithm (Matryoshka Strategy)

Implements the pipe-in-pipe telescoping optimization from specification section 4.1.

Strategy:
1. Sort pipes by diameter descending
2. For each large pipe, find compatible smaller pipes
3. Recursively nest pipes up to max levels
4. Prioritize lighter pipes inside heavier (to protect outer pipe)
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from app.core.calculators.gap_clearance import (
    validate_nesting_compatibility,
    find_compatible_pipes
)
from app.core.calculators.weight_calculator import (
    calculate_bundle_weight,
    HEAVY_EXTRACTION_THRESHOLD_KG
)


logger = logging.getLogger(__name__)


# Maximum nesting levels (from specification section 3.3)
MAX_NESTING_LEVELS = 10  # Increased to support DN800 to DN20 nesting chains


@dataclass
class NestedPipe:
    """Represents a pipe that may contain nested pipes."""
    pipe_data: dict
    nested_pipes: list["NestedPipe"] = field(default_factory=list)
    level: int = 0
    
    @property
    def outer_diameter(self) -> float:
        """Get outer diameter of this pipe."""
        return self.pipe_data.get("outer_diameter_mm") or self.pipe_data.get("dn_mm", 0)
    
    @property
    def inner_diameter(self) -> float:
        """Get inner diameter of this pipe."""
        return self.pipe_data.get("inner_diameter_mm", 0)
    
    @property
    def weight_per_meter(self) -> float:
        """Get weight per meter of this pipe."""
        return self.pipe_data.get("weight_per_meter", 0)
    
    @property
    def total_nesting_levels(self) -> int:
        """Get total depth of nesting."""
        if not self.nested_pipes:
            return 1
        return 1 + max(p.total_nesting_levels for p in self.nested_pipes)
    
    def get_all_pipes(self) -> list[dict]:
        """Get flat list of all pipes in this bundle."""
        pipes = [self.pipe_data]
        for nested in self.nested_pipes:
            pipes.extend(nested.get_all_pipes())
        return pipes
    
    def calculate_bundle_weight(self, pipe_length_m: float) -> float:
        """Calculate total weight of this bundle."""
        return calculate_bundle_weight(self.get_all_pipes(), pipe_length_m)


@dataclass
class NestingResult:
    """Result of the nesting algorithm."""
    bundles: list[NestedPipe]           # Created bundles
    unpacked_pipes: list[dict]           # Pipes that couldn't be nested
    total_pipes_processed: int
    pipes_nested: int
    reduction_ratio: float               # Space reduction estimate


def nest_pipe_recursive(
    host: NestedPipe,
    available_pipes: list[dict],
    max_levels: int = MAX_NESTING_LEVELS,
    current_level: int = 1,
    prefer_lighter: bool = True
) -> tuple[NestedPipe, list[dict]]:
    """
    Recursively nest pipes inside a host pipe.
    
    Args:
        host: The host pipe to nest into
        available_pipes: List of available pipes to try nesting
        max_levels: Maximum nesting depth
        current_level: Current nesting level
        prefer_lighter: Prioritize lighter pipes (to protect host)
        
    Returns:
        Tuple of (updated host, remaining available pipes)
    """
    if current_level >= max_levels:
        return host, available_pipes
    
    if not available_pipes:
        return host, available_pipes
    
    # Find compatible pipes
    compatible = find_compatible_pipes(
        {
            "inner_diameter_mm": host.inner_diameter,
            "outer_diameter_mm": host.outer_diameter
        },
        available_pipes
    )
    
    if not compatible:
        return host, available_pipes
    
    # Sort by weight if preferring lighter
    if prefer_lighter:
        compatible.sort(key=lambda p: p.get("weight_per_meter", 0))
    
    # Only nest one pipe (the best fit - largest that fits)
    # Note: In reality, multiple smaller pipes might fit side-by-side,
    # but that requires circle packing which is handled separately
    best_fit = None
    for pipe in compatible:
        # Re-sort by diameter (largest compatible)
        if best_fit is None or pipe.get("dn_mm", 0) > best_fit.get("dn_mm", 0):
            # But skip if much heavier than host (protect lighter pipes)
            if prefer_lighter:
                host_weight = host.weight_per_meter
                pipe_weight = pipe.get("weight_per_meter", 0)
                if pipe_weight > host_weight * 1.5:  # 50% heavier limit
                    continue
            best_fit = pipe
    
    if not best_fit:
        return host, available_pipes
    
    # Remove selected pipe from available
    remaining = available_pipes.copy()
    
    # helper: find index of first matching pipe by code
    target_code = best_fit.get("code")
    for i, p in enumerate(remaining):
        if p.get("code") == target_code:
            remaining.pop(i)
            break

    
    # Create nested pipe and recurse
    nested = NestedPipe(
        pipe_data=best_fit,
        level=current_level
    )
    
    # Recursively nest into the newly nested pipe
    nested, remaining = nest_pipe_recursive(
        nested,
        remaining,
        max_levels,
        current_level + 1,
        prefer_lighter
    )
    
    host.nested_pipes.append(nested)
    
    return host, remaining


def create_nested_bundles(
    pipes: list[dict],
    pipe_length_m: float = 12.0,
    max_levels: int = MAX_NESTING_LEVELS,
    prefer_lighter: bool = True
) -> NestingResult:
    """
    Create optimized nested bundles from a list of pipes.
    
    Implements the Matryoshka strategy from specification section 4.1:
    1. Sort by diameter descending
    2. Take largest as container
    3. Find largest compatible pipe
    4. Recursively nest
    5. Repeat for remaining pipes
    
    Args:
        pipes: List of pipe dicts with dimensions and weights
        pipe_length_m: Length of pipes (for weight calculation)
        max_levels: Maximum nesting levels
        prefer_lighter: Prioritize lighter pipes inside heavier
        
    Returns:
        NestingResult with bundles and statistics
    """
    if not pipes:
        return NestingResult(
            bundles=[],
            unpacked_pipes=[],
            total_pipes_processed=0,
            pipes_nested=0,
            reduction_ratio=0.0
        )
    
    # Sort by outer diameter descending
    sorted_pipes = sorted(
        pipes,
        key=lambda p: p.get("dn_mm", 0),
        reverse=True
    )
    
    bundles = []
    remaining = sorted_pipes.copy()
    
    while remaining:
        # Take largest pipe as host
        host_data = remaining.pop(0)
        host = NestedPipe(pipe_data=host_data, level=0)
        
        # Try to nest smaller pipes into it
        host, remaining = nest_pipe_recursive(
            host,
            remaining,
            max_levels,
            1,
            prefer_lighter
        )
        
        bundles.append(host)
    
    # Calculate statistics
    total_pipes = len(pipes)
    pipes_in_bundles = sum(len(b.get_all_pipes()) for b in bundles)
    nested_count = sum(len(b.get_all_pipes()) - 1 for b in bundles)
    
    # Estimate space reduction (simplified)
    # Real calculation would use circle packing
    reduction_ratio = nested_count / total_pipes if total_pipes > 0 else 0
    
    result = NestingResult(
        bundles=bundles,
        unpacked_pipes=[],  # All pipes are in bundles (possibly alone)
        total_pipes_processed=total_pipes,
        pipes_nested=nested_count,
        reduction_ratio=reduction_ratio
    )

    logger.debug(
        "nesting.summary",
        extra={
            "bundles": len(bundles),
            "pipes_processed": total_pipes,
            "pipes_nested": nested_count,
            "reduction_ratio": round(reduction_ratio, 3),
        },
    )

    return result


def bundle_to_dict(bundle: NestedPipe, pipe_length_m: float = 12.0) -> dict:
    """Convert a NestedPipe bundle to a serializable dict."""
    return {
        "outer_pipe": bundle.pipe_data,
        "nested_pipes": [
            bundle_to_dict(p, pipe_length_m) 
            for p in bundle.nested_pipes
        ],
        "nesting_levels": bundle.total_nesting_levels,
        "total_pipes": len(bundle.get_all_pipes()),
        "bundle_weight_kg": bundle.calculate_bundle_weight(pipe_length_m),
        "requires_heavy_extraction": (
            bundle.calculate_bundle_weight(pipe_length_m) > HEAVY_EXTRACTION_THRESHOLD_KG
        )
    }
