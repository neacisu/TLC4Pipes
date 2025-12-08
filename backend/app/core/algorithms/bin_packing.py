"""
Bin Packing Algorithm (First Fit Decreasing)

Implements truck loading optimization from specification section 4.1.

Strategy:
1. Sort bundles by weight descending
2. Try to fit each bundle in existing trucks
3. Open new truck if no space/weight available
"""

from dataclasses import dataclass, field
from typing import Optional
from app.core.algorithms.nesting import NestedPipe


@dataclass
class TruckLoad:
    """Represents a loaded truck."""
    truck_number: int
    truck_config: dict
    bundles: list[NestedPipe] = field(default_factory=list)
    
    @property
    def total_weight_kg(self) -> float:
        """Calculate total weight of loaded bundles."""
        return sum(
            b.calculate_bundle_weight(self.pipe_length_m)
            for b in self.bundles
        )
    
    @property
    def pipe_length_m(self) -> float:
        """Get pipe length from truck config (default 12m)."""
        return self.truck_config.get("pipe_length_m", 12.0)
    
    @property
    def max_payload_kg(self) -> int:
        """Get max payload from config."""
        return self.truck_config.get("max_payload_kg", 24000)
    
    @property
    def remaining_capacity_kg(self) -> float:
        """Calculate remaining weight capacity."""
        return self.max_payload_kg - self.total_weight_kg
    
    @property
    def weight_utilization_pct(self) -> float:
        """Calculate weight utilization percentage."""
        return (self.total_weight_kg / self.max_payload_kg) * 100
    
    def can_fit(self, bundle: NestedPipe) -> bool:
        """Check if bundle can fit in this truck (weight only)."""
        bundle_weight = bundle.calculate_bundle_weight(self.pipe_length_m)
        return bundle_weight <= self.remaining_capacity_kg
    
    def add_bundle(self, bundle: NestedPipe) -> bool:
        """Try to add bundle to truck. Returns False if can't fit."""
        if not self.can_fit(bundle):
            return False
        self.bundles.append(bundle)
        return True


@dataclass
class PackingResult:
    """Result of bin packing algorithm."""
    trucks: list[TruckLoad]
    total_trucks_needed: int
    total_weight_kg: float
    average_utilization_pct: float


def first_fit_decreasing(
    bundles: list[NestedPipe],
    truck_config: dict,
    pipe_length_m: float = 12.0
) -> PackingResult:
    """
    Pack bundles into trucks using First Fit Decreasing algorithm.
    
    From specification section 4.1:
    1. Sort bundles by weight descending
    2. For each bundle, find first truck with capacity
    3. If no truck has capacity, open new truck
    
    Args:
        bundles: List of NestedPipe bundles to pack
        truck_config: Truck configuration dict
        pipe_length_m: Pipe length for weight calculations
        
    Returns:
        PackingResult with loaded trucks
    """
    if not bundles:
        return PackingResult(
            trucks=[],
            total_trucks_needed=0,
            total_weight_kg=0.0,
            average_utilization_pct=0.0
        )
    
    # Add pipe length to config
    config = {**truck_config, "pipe_length_m": pipe_length_m}
    
    # Sort bundles by weight descending
    sorted_bundles = sorted(
        bundles,
        key=lambda b: b.calculate_bundle_weight(pipe_length_m),
        reverse=True
    )
    
    trucks: list[TruckLoad] = []
    
    for bundle in sorted_bundles:
        placed = False
        
        # Try to fit in existing truck
        for truck in trucks:
            if truck.add_bundle(bundle):
                placed = True
                break
        
        # Open new truck if needed
        if not placed:
            new_truck = TruckLoad(
                truck_number=len(trucks) + 1,
                truck_config=config
            )
            new_truck.add_bundle(bundle)
            trucks.append(new_truck)
    
    # Calculate statistics
    total_weight = sum(t.total_weight_kg for t in trucks)
    avg_util = sum(t.weight_utilization_pct for t in trucks) / len(trucks) if trucks else 0
    
    return PackingResult(
        trucks=trucks,
        total_trucks_needed=len(trucks),
        total_weight_kg=total_weight,
        average_utilization_pct=avg_util
    )


def pack_pipes_into_trucks(
    pipes: list[dict],
    truck_config: dict,
    pipe_length_m: float = 12.0,
    enable_nesting: bool = True,
    max_nesting_levels: int = 4
) -> PackingResult:
    """
    Complete pipeline: nest pipes then pack into trucks.
    
    Args:
        pipes: List of pipe dicts from order
        truck_config: Truck configuration
        pipe_length_m: Pipe length
        enable_nesting: Whether to apply Matryoshka nesting
        max_nesting_levels: Max nesting depth
        
    Returns:
        PackingResult with optimized truck loads
    """
    from app.core.algorithms.nesting import create_nested_bundles
    
    if enable_nesting:
        # Create nested bundles
        nesting_result = create_nested_bundles(
            pipes,
            pipe_length_m,
            max_nesting_levels
        )
        bundles = nesting_result.bundles
    else:
        # Each pipe is its own bundle
        from app.core.algorithms.nesting import NestedPipe
        bundles = [NestedPipe(pipe_data=p) for p in pipes]
    
    # Apply bin packing
    return first_fit_decreasing(bundles, truck_config, pipe_length_m)


def truck_load_to_dict(truck: TruckLoad) -> dict:
    """Convert TruckLoad to serializable dict."""
    from app.core.algorithms.nesting import bundle_to_dict
    
    return {
        "truck_number": truck.truck_number,
        "total_weight_kg": round(truck.total_weight_kg, 2),
        "weight_utilization_pct": round(truck.weight_utilization_pct, 1),
        "remaining_capacity_kg": round(truck.remaining_capacity_kg, 2),
        "bundle_count": len(truck.bundles),
        "bundles": [
            bundle_to_dict(b, truck.pipe_length_m)
            for b in truck.bundles
        ]
    }
