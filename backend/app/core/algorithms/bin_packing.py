"""
Bin Packing Algorithm (First Fit Decreasing)

Implements truck loading optimization from specification section 4.1.

Strategy:
1. Sort bundles by weight descending
2. Try to fit each bundle in existing trucks
3. Open new truck if no space/weight available
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from app.core.algorithms.nesting import NestedPipe


logger = logging.getLogger(__name__)


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
        """Check if bundle can fit in this truck (weight AND spatial constraints)."""
        bundle_weight = bundle.calculate_bundle_weight(self.pipe_length_m)
        
        # Weight constraint check
        if bundle_weight > self.remaining_capacity_kg:
            return False
        
        # Spatial constraint check - verify bundle fits in truck cross-section
        return self._can_fit_spatially(bundle)
    
    def _can_fit_spatially(self, bundle: NestedPipe) -> bool:
        """Check if bundle fits in truck cross-section with current load."""
        from app.core.geometry.hexagonal_packing import estimate_mixed_stack_height
        
        # Get truck dimensions from config
        truck_height_mm = self.truck_config.get("internal_height_mm", 2700)
        truck_width_mm = self.truck_config.get("internal_width_mm", 2480)
        
        # Collect all bundle diameters including the new one
        diameters = [b.outer_diameter for b in self.bundles]
        diameters.append(bundle.outer_diameter)
        
        # Estimate packed height using hexagonal arrangement
        estimated_height = estimate_mixed_stack_height(diameters, truck_width_mm)
        
        return estimated_height <= truck_height_mm
    
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
    Pack bundles into trucks using First Fit Decreasing algorithm with rebalancing.
    
    From specification section 4.1:
    1. Sort bundles by weight descending
    2. For each bundle, find first truck with capacity
    3. If no truck has capacity, open new truck
    4. Post-process: Try to rebalance to minimize truck count
    
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
            logger.debug("packing.new_truck", extra={"truck_number": new_truck.truck_number})
    
    # POST-PACKING REBALANCING to minimize truck count
    trucks = _rebalance_trucks(trucks, config, pipe_length_m)
    
    # Renumber trucks after potential rebalancing
    for i, truck in enumerate(trucks):
        truck.truck_number = i + 1
    
    # Calculate statistics
    total_weight = sum(t.total_weight_kg for t in trucks)
    avg_util = sum(t.weight_utilization_pct for t in trucks) / len(trucks) if trucks else 0
    
    result = PackingResult(
        trucks=trucks,
        total_trucks_needed=len(trucks),
        total_weight_kg=total_weight,
        average_utilization_pct=avg_util
    )

    logger.debug(
        "packing.summary",
        extra={
            "trucks": len(trucks),
            "total_weight_kg": round(total_weight, 2),
            "avg_util_pct": round(avg_util, 2),
        },
    )

    return result


def _rebalance_trucks(
    trucks: list[TruckLoad],
    config: dict,
    pipe_length_m: float
) -> list[TruckLoad]:
    """
    Try to rebalance bundles between trucks to minimize truck count.
    
    Strategy:
    1. If last truck is partially filled, try to redistribute its bundles
    2. Try moving bundles from last truck to earlier trucks
    3. If last truck becomes empty, remove it
    """
    if len(trucks) <= 1:
        return trucks
    
    max_iterations = 10  # Prevent infinite loops
    
    for _ in range(max_iterations):
        improved = False
        
        # Check if last truck can be eliminated
        last_truck = trucks[-1]
        
        # Try to move each bundle from last truck to earlier trucks
        bundles_to_remove = []
        
        for bundle in last_truck.bundles:
            for truck in trucks[:-1]:  # Try all trucks except the last one
                if truck.can_fit(bundle):
                    # Found a better place
                    bundles_to_remove.append(bundle)
                    truck.bundles.append(bundle)
                    improved = True
                    break
        
        # Remove successfully moved bundles from last truck
        for bundle in bundles_to_remove:
            last_truck.bundles.remove(bundle)
        
        # If last truck is now empty, remove it
        if not last_truck.bundles:
            trucks.pop()
            logger.info("packing.rebalance.truck_eliminated", extra={"eliminated": len(trucks) + 1})
            if len(trucks) <= 1:
                break
            improved = True
        
        if not improved:
            break
    
    # Second pass: Try swapping bundles between trucks for better distribution
    trucks = _optimize_distribution(trucks, config, pipe_length_m)
    
    return trucks


def _optimize_distribution(
    trucks: list[TruckLoad],
    config: dict,
    pipe_length_m: float
) -> list[TruckLoad]:
    """
    Optimize bundle distribution for balanced weight/volume usage.
    
    Try to swap bundles between trucks to improve overall utilization.
    """
    if len(trucks) <= 1:
        return trucks
    
    max_iterations = 20
    
    for _ in range(max_iterations):
        improved = False
        
        # Try to find swaps that improve utilization balance
        for i, truck_a in enumerate(trucks[:-1]):
            for j, truck_b in enumerate(trucks[i+1:], start=i+1):
                # Try moving bundles from less loaded to more loaded truck
                # if it helps balance without exceeding limits
                swap_result = _try_balance_pair(truck_a, truck_b)
                if swap_result:
                    improved = True
        
        if not improved:
            break
    
    return trucks


def _try_balance_pair(truck_a: TruckLoad, truck_b: TruckLoad) -> bool:
    """
    Try to balance load between two trucks.
    
    Returns True if any improvement was made.
    """
    # Calculate current utilizations
    util_a = truck_a.weight_utilization_pct
    util_b = truck_b.weight_utilization_pct
    
    # If already balanced (within 15%), don't bother
    if abs(util_a - util_b) < 15:
        return False
    
    # Try moving small bundles from heavier truck to lighter
    if util_a > util_b:
        source, target = truck_a, truck_b
    else:
        source, target = truck_b, truck_a
    
    # Sort bundles by weight ascending (try smaller ones first)
    sorted_bundles = sorted(
        source.bundles,
        key=lambda b: b.calculate_bundle_weight(source.pipe_length_m)
    )
    
    moved = False
    for bundle in sorted_bundles:
        if target.can_fit(bundle):
            # Check if this improves balance
            new_source_weight = source.total_weight_kg - bundle.calculate_bundle_weight(source.pipe_length_m)
            new_target_weight = target.total_weight_kg + bundle.calculate_bundle_weight(target.pipe_length_m)
            
            old_diff = abs(source.total_weight_kg - target.total_weight_kg)
            new_diff = abs(new_source_weight - new_target_weight)
            
            if new_diff < old_diff * 0.9:  # Require 10% improvement
                source.bundles.remove(bundle)
                target.bundles.append(bundle)
                moved = True
                break
    
    return moved


def pack_pipes_into_trucks(
    pipes: list[dict],
    truck_config: dict,
    pipe_length_m: float = 12.0,
    enable_nesting: bool = True,
    max_nesting_levels: int = 4
) -> PackingResult:
    """
    Advanced optimization: Minimize trucks first, then nest within each truck.
    
    Strategy (Truck-First with Per-Truck Nesting):
    1. Calculate total weight and minimum trucks needed
    2. Distribute pipes to trucks optimally (balance weight AND volume)
    3. Apply nesting WITHIN each truck's allocation
    4. This ensures minimum truck count with optimal nesting
    
    Args:
        pipes: List of pipe dicts from order
        truck_config: Truck configuration
        pipe_length_m: Pipe length
        enable_nesting: Whether to apply Matryoshka nesting
        max_nesting_levels: Max nesting depth
        
    Returns:
        PackingResult with optimized truck loads
    """
    from app.core.algorithms.nesting import create_nested_bundles, NestedPipe
    
    if not pipes:
        return PackingResult(
            trucks=[],
            total_trucks_needed=0,
            total_weight_kg=0.0,
            average_utilization_pct=0.0
        )
    
    config = {**truck_config, "pipe_length_m": pipe_length_m}
    max_payload = truck_config.get("max_payload_kg", 24000)
    
    # Calculate total weight of all pipes
    total_weight = sum(
        p.get("weight_per_meter", 0) * pipe_length_m 
        for p in pipes
    )
    
    # Calculate minimum trucks needed based on weight
    min_trucks_by_weight = max(1, int((total_weight / max_payload) + 0.99))  # Ceiling
    
    logger.info(
        "packing.strategy.truck_first",
        extra={
            "total_pipes": len(pipes),
            "total_weight_kg": round(total_weight, 2),
            "min_trucks_estimate": min_trucks_by_weight
        }
    )
    
    # Try progressively more trucks until we find a valid solution
    for num_trucks in range(min_trucks_by_weight, min_trucks_by_weight + 5):
        result = _try_pack_with_n_trucks(
            pipes, config, pipe_length_m, num_trucks, 
            enable_nesting, max_nesting_levels
        )
        if result is not None:
            logger.info(
                "packing.strategy.success",
                extra={"trucks_used": num_trucks, "attempted": num_trucks - min_trucks_by_weight + 1}
            )
            return result
    
    # Fallback to standard FFD if optimization fails
    logger.warning("packing.strategy.fallback_to_ffd")
    if enable_nesting:
        nesting_result = create_nested_bundles(pipes, pipe_length_m, max_nesting_levels)
        bundles = nesting_result.bundles
    else:
        bundles = [NestedPipe(pipe_data=p) for p in pipes]
    
    return first_fit_decreasing(bundles, truck_config, pipe_length_m)


def _try_pack_with_n_trucks(
    pipes: list[dict],
    config: dict,
    pipe_length_m: float,
    n_trucks: int,
    enable_nesting: bool,
    max_nesting_levels: int
) -> Optional[PackingResult]:
    """
    Try to pack all pipes into exactly n trucks.
    
    Returns PackingResult if successful, None if impossible.
    """
    from app.core.algorithms.nesting import create_nested_bundles, NestedPipe
    
    max_payload = config.get("max_payload_kg", 24000)
    target_weight_per_truck = sum(
        p.get("weight_per_meter", 0) * pipe_length_m for p in pipes
    ) / n_trucks
    
    # Sort pipes by diameter descending (larger pipes first for better nesting)
    sorted_pipes = sorted(
        pipes,
        key=lambda p: (p.get("dn_mm", 0), p.get("weight_per_meter", 0)),
        reverse=True
    )
    
    # Distribute pipes to trucks trying to balance weight
    truck_pipes: list[list[dict]] = [[] for _ in range(n_trucks)]
    truck_weights: list[float] = [0.0] * n_trucks
    
    for pipe in sorted_pipes:
        pipe_weight = pipe.get("weight_per_meter", 0) * pipe_length_m
        
        # Fill trucks sequentially - first truck that has space gets the pipe
        # This ensures we fill earlier trucks before opening new ones
        placed = False
        for i in range(n_trucks):
            if truck_weights[i] + pipe_weight <= max_payload:
                truck_pipes[i].append(pipe)
                truck_weights[i] += pipe_weight
                placed = True
                break
        
        if not placed:
            # Can't fit this pipe anywhere - need more trucks
            return None
    
    # Now apply nesting WITHIN each truck's pipe allocation
    trucks: list[TruckLoad] = []
    
    for i, pipes_for_truck in enumerate(truck_pipes):
        if not pipes_for_truck:
            continue
            
        if enable_nesting:
            # Nest only the pipes assigned to THIS truck
            nesting_result = create_nested_bundles(
                pipes_for_truck,
                pipe_length_m,
                max_nesting_levels
            )
            bundles = nesting_result.bundles
        else:
            bundles = [NestedPipe(pipe_data=p) for p in pipes_for_truck]
        
        # Create truck and add bundles
        truck = TruckLoad(
            truck_number=i + 1,
            truck_config=config
        )
        
        # Validate bundles fit spatially
        for bundle in bundles:
            if not truck.add_bundle(bundle):
                # Spatial constraint violated - need more trucks
                logger.debug(
                    "packing.spatial_fail",
                    extra={"truck": i + 1, "bundle_diameter": bundle.outer_diameter}
                )
                return None
        
        trucks.append(truck)
    
    # Calculate statistics
    total_weight = sum(t.total_weight_kg for t in trucks)
    avg_util = sum(t.weight_utilization_pct for t in trucks) / len(trucks) if trucks else 0
    
    return PackingResult(
        trucks=trucks,
        total_trucks_needed=len(trucks),
        total_weight_kg=total_weight,
        average_utilization_pct=avg_util
    )


def truck_load_to_dict(truck: TruckLoad) -> dict:
    """Convert TruckLoad to serializable dict."""
    from app.core.algorithms.nesting import bundle_to_dict
    
    return {
        "truck_number": truck.truck_number,
        "total_weight_kg": round(truck.total_weight_kg, 2),
        "current_payload_kg": round(truck.total_weight_kg, 2),  # Alias for frontend compatibility
        "weight_utilization_pct": round(truck.weight_utilization_pct, 1),
        "remaining_capacity_kg": round(truck.remaining_capacity_kg, 2),
        "max_payload_kg": truck.max_payload_kg,
        "bundle_count": len(truck.bundles),
        "bundles": [
            bundle_to_dict(b, truck.pipe_length_m)
            for b in truck.bundles
        ]
    }
