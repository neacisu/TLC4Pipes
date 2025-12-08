"""
Loading Service - Orchestrates loading calculation workflow

Main entry point for loading optimization:
1. Fetch order items with pipe data
2. Apply Matryoshka nesting
3. Apply bin packing to trucks
4. Calculate metrics and generate plan
"""

import logging
from typing import Optional
from dataclasses import dataclass

from app.core.algorithms.nesting import (
    create_nested_bundles,
    bundle_to_dict,
    NestingResult
)
from app.core.algorithms.bin_packing import (
    pack_pipes_into_trucks,
    truck_load_to_dict,
    PackingResult
)
from app.core.calculators.weight_calculator import (
    calculate_order_total_weight,
    check_weight_limits
)


logger = logging.getLogger(__name__)


@dataclass
class LoadingPlanResult:
    """Complete loading plan result."""
    order_id: int
    pipe_length_m: float
    total_pipes: int
    total_weight_kg: float
    trucks_needed: int
    trucks: list[dict]
    nesting_stats: dict
    weight_limits: dict
    warnings: list[str]


def calculate_loading_plan(
    order_items: list[dict],
    truck_config: dict,
    pipe_length_m: float = 12.0,
    enable_nesting: bool = True,
    max_nesting_levels: int = 4,
    order_id: Optional[int] = None
) -> LoadingPlanResult:
    """
    Calculate optimized loading plan for an order.
    
    Args:
        order_items: List of order items with pipe data
            Each item: {pipe_id, code, dn_mm, inner_diameter_mm, weight_per_meter, quantity}
        truck_config: Truck configuration dict
        pipe_length_m: Pipe length (12, 12.5, or 13 meters)
        enable_nesting: Whether to apply telescoping
        max_nesting_levels: Maximum nesting depth
        order_id: Optional order ID for reference
        
    Returns:
        LoadingPlanResult with complete plan
    """
    warnings = []
    logger.info(
        "loading.calculate.start",
        extra={
            "items": len(order_items),
            "pipe_length_m": pipe_length_m,
            "enable_nesting": enable_nesting,
            "max_nesting_levels": max_nesting_levels,
        },
    )
    
    # Expand order items to individual pipes
    pipes = []
    for item in order_items:
        for _ in range(item.get("quantity", 1)):
            # Each pipe needs outer_diameter for gap calculations
            pipe = {
                **item,
                "outer_diameter_mm": item.get("dn_mm", 0)  # DN is outer diameter
            }
            pipes.append(pipe)
    
    total_pipes = len(pipes)
    
    # Calculate total weight before optimization
    total_weight = calculate_order_total_weight(order_items, pipe_length_m)
    
    # Check weight limits
    weight_limits = check_weight_limits(total_weight, truck_config.get("max_payload_kg", 24000))
    
    # Apply nesting and packing
    packing_result = pack_pipes_into_trucks(
        pipes,
        truck_config,
        pipe_length_m,
        enable_nesting,
        max_nesting_levels
    )
    
    # Convert trucks to dicts
    trucks = [truck_load_to_dict(t) for t in packing_result.trucks]
    
    # Check for heavy extraction warnings
    for truck in trucks:
        for bundle in truck.get("bundles", []):
            if bundle.get("requires_heavy_extraction"):
                warnings.append(
                    f"Truck {truck['truck_number']}: Bundle with {bundle['outer_pipe'].get('code')} "
                    f"weighs {bundle['bundle_weight_kg']:.0f}kg - requires heavy equipment"
                )
    
    # Add overweight warning if applicable
    if not weight_limits["is_valid"]:
        warnings.append(
            f"Order exceeds single truck capacity by {weight_limits['overweight_kg']:.0f}kg"
        )
        logger.warning(
            "loading.weight.overlimit",
            extra={"total_weight_kg": round(total_weight, 2), "overweight_kg": round(weight_limits['overweight_kg'], 2)},
        )
    
    # Calculate nesting stats
    nested_count = sum(
        sum(1 for b in t.get("bundles", []) if b.get("nesting_levels", 1) > 1)
        for t in trucks
    )
    
    nesting_stats = {
        "nesting_enabled": enable_nesting,
        "bundles_with_nesting": nested_count,
        "max_levels_used": max(
            max((b.get("nesting_levels", 1) for b in t.get("bundles", [])), default=1)
            for t in trucks
        ) if trucks else 0,
        "estimated_space_reduction_pct": round(
            (1 - len(trucks) / max(1, len(order_items))) * 100, 1
        ) if enable_nesting else 0
    }
    
    result = LoadingPlanResult(
        order_id=order_id or 0,
        pipe_length_m=pipe_length_m,
        total_pipes=total_pipes,
        total_weight_kg=round(total_weight, 2),
        trucks_needed=len(trucks),
        trucks=trucks,
        nesting_stats=nesting_stats,
        weight_limits=weight_limits,
        warnings=warnings
    )

    logger.info(
        "loading.calculate.done",
        extra={
            "trucks": len(trucks),
            "total_weight_kg": result.total_weight_kg,
            "warnings": len(warnings),
        },
    )

    return result


def loading_plan_to_dict(result: LoadingPlanResult) -> dict:
    """Convert LoadingPlanResult to serializable dict."""
    return {
        "order_id": result.order_id,
        "pipe_length_m": result.pipe_length_m,
        "summary": {
            "total_pipes": result.total_pipes,
            "total_weight_kg": result.total_weight_kg,
            "trucks_needed": result.trucks_needed,
        },
        "trucks": result.trucks,
        "nesting_stats": result.nesting_stats,
        "weight_limits": result.weight_limits,
        "warnings": result.warnings
    }


async def calculate_loading_plan_from_db(
    order_id: int,
    db_session,
    truck_config_id: Optional[int] = None
) -> LoadingPlanResult:
    """
    Calculate loading plan from database order.
    
    Args:
        order_id: Order ID to load
        db_session: Database session
        truck_config_id: Optional truck config ID (uses default if not provided)
        
    Returns:
        LoadingPlanResult
    """
    from sqlalchemy import select
    from app.models import Order, OrderItem, PipeCatalog, TruckConfig
    
    # Load order with items
    order_query = select(Order).where(Order.id == order_id)
    order = (await db_session.execute(order_query)).scalar_one_or_none()
    
    if not order:
        logger.error("loading.order_missing", extra={"order_id": order_id})
        raise ValueError(f"Order {order_id} not found")
    
    # Load order items with pipe data
    items_query = (
        select(OrderItem, PipeCatalog)
        .join(PipeCatalog, OrderItem.pipe_id == PipeCatalog.id)
        .where(OrderItem.order_id == order_id)
    )
    items_result = await db_session.execute(items_query)
    
    order_items = []
    for item, pipe in items_result:
        order_items.append({
            "pipe_id": pipe.id,
            "code": pipe.code,
            "dn_mm": pipe.dn_mm,
            "sdr": pipe.sdr,
            "pn_class": pipe.pn_class,
            "inner_diameter_mm": float(pipe.inner_diameter_mm),
            "wall_mm": float(pipe.wall_mm),
            "weight_per_meter": float(pipe.weight_per_meter),
            "quantity": item.quantity
        })
    
    # Load truck config
    if truck_config_id:
        truck_query = select(TruckConfig).where(TruckConfig.id == truck_config_id)
    else:
        truck_query = select(TruckConfig).limit(1)  # Default truck
    
    truck = (await db_session.execute(truck_query)).scalar_one_or_none()
    
    truck_config = {
        "name": truck.name if truck else "Standard 24t Romania",
        "max_payload_kg": truck.max_payload_kg if truck else 24000,
        "internal_length_mm": truck.internal_length_mm if truck else 13600,
        "internal_width_mm": truck.internal_width_mm if truck else 2480,
        "internal_height_mm": truck.internal_height_mm if truck else 2700,
    }
    
    return calculate_loading_plan(
        order_items,
        truck_config,
        float(order.pipe_length_m),
        enable_nesting=True,
        order_id=order_id
    )
