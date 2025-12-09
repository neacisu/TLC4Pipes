"""
Order Service

Business logic for order management.
"""

import logging
from typing import List, Optional, Tuple
import math
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem
from app.models.pipe_catalog import PipeCatalog


logger = logging.getLogger(__name__)


async def create_order(
    session: AsyncSession,
    pipe_length_m: float = 12.0,
    order_number: Optional[str] = None
) -> Order:
    """
    Create a new order.
    
    Args:
        session: Database session
        pipe_length_m: Pipe length for order
        order_number: Optional order number (auto-generated if not provided)
        
    Returns:
        Created Order
    """
    import uuid
    
    if order_number is None:
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    order = Order(
        order_number=order_number,
        pipe_length_m=pipe_length_m,
        status="draft"
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)

    logger.info("order.created", extra={"order_id": order.id, "order_number": order.order_number})
    
    return order


async def add_order_item(
    session: AsyncSession,
    order_id: int,
    pipe_id: int,
    quantity: Optional[int] = None,
    total_meters: Optional[float] = None
) -> Tuple[OrderItem, Optional[str]]:
    """
    Add an item to an order.
    
    Args:
        session: Database session
        order_id: Order ID
        pipe_id: Pipe catalog ID
        quantity: Number of pipes
        
    Returns:
        Tuple of (OrderItem, error_message)
    """
    # Verify order exists
    order_query = select(Order).where(Order.id == order_id)
    order = (await session.execute(order_query)).scalar_one_or_none()
    
    if not order:
        logger.warning("order.add_item.order_missing", extra={"order_id": order_id})
        return None, f"Order {order_id} not found"
    
    # Verify pipe exists
    pipe_query = select(PipeCatalog).where(PipeCatalog.id == pipe_id)
    pipe = (await session.execute(pipe_query)).scalar_one_or_none()
    
    if not pipe:
        logger.warning("order.add_item.pipe_missing", extra={"order_id": order_id, "pipe_id": pipe_id})
        return None, f"Pipe {pipe_id} not found in catalog"
    
    # Derive quantity if provided as meters
    ordered_meters_value = None
    pipe_count_value = None
    if total_meters is not None:
        ordered_meters_value = float(total_meters)
        computed_qty = math.ceil(ordered_meters_value / float(order.pipe_length_m))
        pipe_count_value = max(computed_qty, 1)
        quantity = pipe_count_value

    if quantity is None:
        logger.warning(
            "order.add_item.quantity_missing",
            extra={"order_id": order_id, "pipe_id": pipe_id, "total_meters": total_meters},
        )
        return None, "Quantity is required"

    # If quantity was provided directly (no meters), store pipe_count = quantity
    if pipe_count_value is None:
        pipe_count_value = quantity

    # Calculate line weight using quantity derived above
    line_weight = float(pipe.weight_per_meter) * float(order.pipe_length_m) * quantity
    
    # Create item
    item = OrderItem(
        order_id=order_id,
        pipe_id=pipe_id,
        quantity=quantity,
        ordered_meters=ordered_meters_value,
        pipe_count=pipe_count_value,
        line_weight_kg=line_weight
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    
    # Update order totals
    await update_order_totals(session, order_id)

    logger.info(
        "order.add_item.success",
        extra={
            "order_id": order_id,
            "pipe_id": pipe_id,
            "quantity": quantity,
            "line_weight_kg": round(line_weight, 2),
        },
    )
    
    return item, None


async def update_order_totals(session: AsyncSession, order_id: int) -> None:
    """
    Recalculate order totals from items.
    
    Args:
        session: Database session
        order_id: Order ID
    """
    # Load order with items
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order = (await session.execute(query)).scalar_one_or_none()
    
    if not order:
        logger.debug("order.totals.order_missing", extra={"order_id": order_id})
        return
    
    # Calculate totals
    total_pipes = sum(item.quantity for item in order.items)
    total_weight = sum(float(item.line_weight_kg or 0) for item in order.items)
    
    order.total_pipes = total_pipes
    order.total_weight_kg = total_weight
    
    await session.commit()
    logger.debug(
        "order.totals.updated",
        extra={"order_id": order_id, "total_pipes": total_pipes, "total_weight_kg": round(total_weight, 2)},
    )


async def get_order_with_items(
    session: AsyncSession,
    order_id: int
) -> Optional[dict]:
    """
    Get order with all items and pipe details.
    
    Args:
        session: Database session
        order_id: Order ID
        
    Returns:
        Dict with order and items, or None
    """
    query = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.pipe))
        .where(Order.id == order_id)
    )
    order = (await session.execute(query)).scalar_one_or_none()
    
    if not order:
        logger.debug("order.get.not_found", extra={"order_id": order_id})
        return None
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "pipe_length_m": float(order.pipe_length_m),
        "status": order.status,
        "total_pipes": order.total_pipes,
        "total_weight_kg": float(order.total_weight_kg) if order.total_weight_kg else 0,
        "items": [
            {
                "id": item.id,
                "pipe_id": item.pipe_id,
                "pipe_code": item.pipe.code if item.pipe else None,
                "dn_mm": item.pipe.dn_mm if item.pipe else None,
                "pn_class": item.pipe.pn_class if item.pipe else None,
                "quantity": item.quantity,
                "ordered_meters": float(item.ordered_meters) if item.ordered_meters else None,
                "pipe_count": item.pipe_count,
                "line_weight_kg": float(item.line_weight_kg) if item.line_weight_kg else 0
            }
            for item in order.items
        ]
    }


async def list_orders(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    statuses: Optional[List[str]] = None
) -> List[dict]:
    """
    List orders with pagination.
    
    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        status: Optional status filter
        
    Returns:
        List of order dicts
    """
    query = select(Order)

    if statuses:
        query = query.where(Order.status.in_(statuses))
    
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
    
    result = await session.execute(query)
    orders = result.scalars().all()
    
    return [
        {
            "id": o.id,
            "order_number": o.order_number,
            "pipe_length_m": float(o.pipe_length_m),
            "status": o.status,
            "total_pipes": o.total_pipes,
            "total_weight_kg": float(o.total_weight_kg) if o.total_weight_kg else 0,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]


async def delete_order(session: AsyncSession, order_id: int) -> bool:
    """
    Delete an order and its items.
    
    Args:
        session: Database session
        order_id: Order ID
        
    Returns:
        True if deleted, False if not found
    """
    query = select(Order).where(Order.id == order_id)
    order = (await session.execute(query)).scalar_one_or_none()
    
    if not order:
        logger.warning("order.delete.not_found", extra={"order_id": order_id})
        return False
    
    await session.delete(order)
    await session.commit()
    logger.info("order.deleted", extra={"order_id": order_id})
    return True


async def delete_order_item(
    session: AsyncSession,
    order_id: int,
    item_id: int
) -> bool:
    """
    Delete a specific item from an order.
    
    Args:
        session: Database session
        order_id: Order ID
        item_id: Item ID
        
    Returns:
        True if deleted, False if not found
    """
    query = select(OrderItem).where(
        OrderItem.id == item_id,
        OrderItem.order_id == order_id
    )
    item = (await session.execute(query)).scalar_one_or_none()
    
    if not item:
        logger.warning("order.delete_item.not_found", extra={"order_id": order_id, "item_id": item_id})
        return False
    
    await session.delete(item)
    await session.commit()
    
    # Update order totals
    await update_order_totals(session, order_id)
    
    logger.info("order.delete_item.success", extra={"order_id": order_id, "item_id": item_id})
    return True


async def update_order_status(
    session: AsyncSession,
    order_id: int,
    status: str
) -> Optional[Order]:
    """
    Update order status.
    
    Valid statuses: draft, processing, calculated, completed, cancelled
    
    Args:
        session: Database session
        order_id: Order ID
        status: New status
        
    Returns:
        Updated order or None
    """
    valid_statuses = ["draft", "processing", "calculated", "completed", "cancelled"]
    if status not in valid_statuses:
        logger.warning("order.status.invalid", extra={"order_id": order_id, "status": status})
        return None
    
    query = select(Order).where(Order.id == order_id)
    order = (await session.execute(query)).scalar_one_or_none()
    
    if not order:
        logger.warning("order.status.not_found", extra={"order_id": order_id})
        return None
    
    order.status = status
    await session.commit()
    logger.info("order.status.updated", extra={"order_id": order_id, "status": status})
    return order


async def create_order_from_csv(
    session: AsyncSession,
    parsed_items: List[dict],
    pipe_length_m: float = 12.0
) -> Tuple[Optional[Order], List[str]]:
    """
    Create order from parsed CSV data.
    
    Args:
        session: Database session
        parsed_items: List of dicts with dn_mm, pn_class, quantity
        pipe_length_m: Pipe length
        
    Returns:
        Tuple of (Order, error_messages)
    """
    errors = []
    
    # Create order
    order = await create_order(session, pipe_length_m)
    
    # Match parsed items to pipe catalog
    for item in parsed_items:
        dn = item.get('dn_mm')
        pn = item.get('pn_class')
        qty = item.get('quantity', 1)
        
        # Find pipe in catalog
        pipe_query = select(PipeCatalog).where(
            PipeCatalog.dn_mm == dn,
            PipeCatalog.pn_class == pn
        )
        pipe = (await session.execute(pipe_query)).scalar_one_or_none()
        
        if not pipe:
            msg = f"Pipe DN{dn} {pn} not found in catalog"
            errors.append(msg)
            logger.warning("order.csv.pipe_missing", extra={"order_id": order.id, "dn": dn, "pn": pn})
            continue
        
        _, error = await add_order_item(session, order.id, pipe.id, qty)
        if error:
            errors.append(error)
            logger.warning("order.csv.add_item_failed", extra={"order_id": order.id, "pipe_id": pipe.id, "error": error})
    
    return order, errors
