"""
Orders API Routes
CRUD operations for loading orders
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from app.api.schemas.order import OrderResponse, OrderCreate, OrderItemCreate
from app.services.order_service import (
    create_order,
    add_order_item,
    get_order_with_items,
    list_orders,
    delete_order,
    update_order_status,
    create_order_from_csv,
)
from app.utils.csv_parser import parse_csv_bytes, validate_parsed_items

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all orders with pagination.
    
    Status values: draft, processing, calculated, completed
    """
    orders = await list_orders(db, skip, limit, status)
    logger.debug("orders.list", extra={"skip": skip, "limit": limit, "status": status})
    return {"orders": orders, "count": len(orders)}


@router.get("/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific order with all items.
    """
    order = await get_order_with_items(db, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order


@router.post("/")
async def create_new_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new loading order.
    """
    new_order = await create_order(
        db,
        pipe_length_m=float(order.pipe_length_m),
        order_number=None  # Auto-generate
    )
    
    # Add items if provided
    errors = []
    for item in order.items:
        result, error = await add_order_item(
            db, new_order.id, item.pipe_id, item.quantity
        )
        if error:
            errors.append(error)
    
    # Refresh order to get updated totals
    final_order = await get_order_with_items(db, new_order.id)
    
    logger.info(
        "orders.create",
        extra={"order_id": final_order["id"] if final_order else None, "errors": len(errors)},
    )

    return {
        "order": final_order,
        "errors": errors if errors else None
    }


@router.post("/{order_id}/items")
async def add_item_to_order(
    order_id: int,
    item: OrderItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a pipe item to an existing order.
    """
    result, error = await add_order_item(db, order_id, item.pipe_id, item.quantity)
    
    if error:
        logger.warning("orders.add_item.failed", extra={"order_id": order_id, "pipe_id": item.pipe_id, "error": error})
        raise HTTPException(status_code=400, detail=error)
    
    logger.info("orders.add_item.success", extra={"order_id": order_id, "pipe_id": item.pipe_id})
    return {
        "message": "Item added successfully",
        "item": {
            "id": result.id,
            "pipe_id": result.pipe_id,
            "quantity": result.quantity,
            "line_weight_kg": float(result.line_weight_kg) if result.line_weight_kg else 0
        }
    }


@router.patch("/{order_id}/status")
async def update_status(
    order_id: int,
    status: str = Query(..., description="New status"),
    db: AsyncSession = Depends(get_db),
):
    """
    Update order status.
    
    Valid statuses: draft, processing, calculated, completed
    """
    valid_statuses = ["draft", "processing", "calculated", "completed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    order = await update_order_status(db, order_id, status)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    logger.info("orders.status.updated", extra={"order_id": order_id, "status": status})
    return {"message": f"Status updated to {status}", "order_id": order_id}


@router.delete("/{order_id}")
async def delete_existing_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an order and all its items.
    """
    deleted = await delete_order(db, order_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    
    logger.info("orders.deleted", extra={"order_id": order_id})
    return {"message": "Order deleted successfully", "order_id": order_id}


@router.post("/import-csv")
async def import_order_from_csv(
    file: UploadFile = File(...),
    pipe_length_m: float = Query(12.0, ge=6, le=18),
    db: AsyncSession = Depends(get_db),
):
    """
    Import order from CSV file.
    
    Expected CSV columns (flexible naming):
    - DN / Diameter / dn_mm
    - PN / Pressure / pn_class / SDR
    - Quantity / qty / cantitate
    
    Example:
    ```
    DN,PN,Quantity
    200,PN6,10
    315,PN10,5
    ```
    """
    # Read file
    content = await file.read()
    
    # Parse CSV
    parse_result = parse_csv_bytes(content)
    
    if parse_result.errors and not parse_result.items:
        logger.warning("orders.import.parse_failed", extra={"errors": parse_result.errors})
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Failed to parse CSV",
                "errors": parse_result.errors
            }
        )
    
    # Validate against catalog
    valid_items, validation_errors = validate_parsed_items(parse_result.items)
    
    if not valid_items:
        logger.warning(
            "orders.import.validation_failed",
            extra={"parse_errors": len(parse_result.errors), "validation_errors": len(validation_errors)},
        )
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No valid items in CSV",
                "parse_errors": parse_result.errors,
                "validation_errors": validation_errors
            }
        )
    
    # Convert to dicts for service
    items_dicts = [
        {
            "dn_mm": item.dn_mm,
            "pn_class": item.pn_class,
            "quantity": item.quantity
        }
        for item in valid_items
    ]
    
    # Create order
    order, create_errors = await create_order_from_csv(
        db, items_dicts, pipe_length_m
    )
    
    # Get full order details
    final_order = await get_order_with_items(db, order.id)
    
    all_errors = parse_result.errors + validation_errors + create_errors
    logger.info(
        "orders.import_csv.completed",
        extra={
            "order_id": order.id,
            "rows": parse_result.total_rows,
            "valid": parse_result.valid_rows,
            "warnings": len(parse_result.warnings),
            "errors": len(all_errors),
        },
    )
    
    return {
        "order": final_order,
        "import_summary": {
            "total_rows": parse_result.total_rows,
            "valid_rows": parse_result.valid_rows,
            "imported_items": len(valid_items),
        },
        "warnings": parse_result.warnings if parse_result.warnings else None,
        "errors": all_errors if all_errors else None
    }
