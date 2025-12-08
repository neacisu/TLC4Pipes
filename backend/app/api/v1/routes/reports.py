"""
Reports API Routes
PDF report generation and loading summaries
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import io

from database.connection import get_db
from app.models.loading_plan import LoadingPlan
from app.models.order import Order
from app.services.report_service import (
    generate_loading_report_pdf,
    generate_summary_data,
    LoadingReportData,
    REPORTLAB_AVAILABLE
)
from app.services.loading_service import (
    calculate_loading_plan,
    loading_plan_to_dict
)

router = APIRouter()


@router.get("/generate/{order_id}")
async def generate_report_for_order(
    order_id: int,
    truck_config_id: Optional[int] = Query(None),
    pipe_length_m: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate loading report for an order.
    
    Returns loading plan calculation and summary data.
    """
    from sqlalchemy.orm import selectinload
    from app.models.order import Order, OrderItem
    from app.models.pipe_catalog import PipeCatalog
    from app.models.truck_config import TruckConfig
    
    # Load order with items
    order_query = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.pipe))
        .where(Order.id == order_id)
    )
    order = (await db.execute(order_query)).scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Use order's pipe length if not overridden
    length = pipe_length_m or float(order.pipe_length_m)
    
    # Build order items for calculation
    order_items = []
    for item in order.items:
        if item.pipe:
            order_items.append({
                "pipe_id": item.pipe.id,
                "code": item.pipe.code,
                "dn_mm": item.pipe.dn_mm,
                "sdr": item.pipe.sdr,
                "pn_class": item.pipe.pn_class,
                "inner_diameter_mm": float(item.pipe.inner_diameter_mm),
                "wall_mm": float(item.pipe.wall_mm),
                "weight_per_meter": float(item.pipe.weight_per_meter),
                "quantity": item.quantity
            })
    
    if not order_items:
        raise HTTPException(status_code=400, detail="Order has no valid items")
    
    # Load truck config
    if truck_config_id:
        truck_query = select(TruckConfig).where(TruckConfig.id == truck_config_id)
    else:
        truck_query = select(TruckConfig).limit(1)
    
    truck = (await db.execute(truck_query)).scalar_one_or_none()
    
    truck_config = {
        "name": truck.name if truck else "Standard 24t Romania",
        "max_payload_kg": truck.max_payload_kg if truck else 24000,
        "internal_length_mm": truck.internal_length_mm if truck else 13600,
        "internal_width_mm": truck.internal_width_mm if truck else 2480,
        "internal_height_mm": truck.internal_height_mm if truck else 2700,
    }
    
    # Calculate loading plan
    plan = calculate_loading_plan(
        order_items,
        truck_config,
        length,
        enable_nesting=True,
        order_id=order_id
    )
    
    result = loading_plan_to_dict(plan)
    summary = generate_summary_data(result)
    
    return {
        "order_id": order_id,
        "order_number": order.order_number,
        "pipe_length_m": length,
        "loading_plan": result,
        "summary": summary
    }


@router.get("/pdf/{order_id}")
async def generate_pdf_report(
    order_id: int,
    truck_config_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate PDF loading report (Loading Ticket).
    
    Returns downloadable PDF file.
    """
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="PDF generation requires ReportLab. Install with: pip install reportlab"
        )
    
    # Get report data (reuse logic from generate endpoint)
    from sqlalchemy.orm import selectinload
    from app.models.order import Order, OrderItem
    from app.models.truck_config import TruckConfig
    
    order_query = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.pipe))
        .where(Order.id == order_id)
    )
    order = (await db.execute(order_query)).scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    length = float(order.pipe_length_m)
    
    # Build order items
    order_items = []
    for item in order.items:
        if item.pipe:
            order_items.append({
                "pipe_id": item.pipe.id,
                "code": item.pipe.code,
                "dn_mm": item.pipe.dn_mm,
                "sdr": item.pipe.sdr,
                "pn_class": item.pipe.pn_class,
                "inner_diameter_mm": float(item.pipe.inner_diameter_mm),
                "wall_mm": float(item.pipe.wall_mm),
                "weight_per_meter": float(item.pipe.weight_per_meter),
                "quantity": item.quantity
            })
    
    if not order_items:
        raise HTTPException(status_code=400, detail="Order has no valid items")
    
    # Load truck config
    if truck_config_id:
        truck_query = select(TruckConfig).where(TruckConfig.id == truck_config_id)
    else:
        truck_query = select(TruckConfig).limit(1)
    
    truck = (await db.execute(truck_query)).scalar_one_or_none()
    
    truck_config = {
        "name": truck.name if truck else "Standard 24t Romania",
        "max_payload_kg": truck.max_payload_kg if truck else 24000,
        "internal_length_mm": truck.internal_length_mm if truck else 13600,
        "internal_width_mm": truck.internal_width_mm if truck else 2480,
        "internal_height_mm": truck.internal_height_mm if truck else 2700,
    }
    
    # Calculate plan
    plan = calculate_loading_plan(
        order_items,
        truck_config,
        length,
        enable_nesting=True,
        order_id=order_id
    )
    
    result = loading_plan_to_dict(plan)
    
    # Create report data
    report_data = LoadingReportData(
        order_number=order.order_number,
        pipe_length_m=length,
        total_pipes=plan.total_pipes,
        total_weight_kg=plan.total_weight_kg,
        trucks=result["trucks"],
        nesting_stats=result["nesting_stats"],
        generated_at=datetime.now()
    )
    
    # Generate PDF
    pdf_bytes = generate_loading_report_pdf(report_data)
    
    # Return as downloadable file
    filename = f"loading_plan_{order.order_number}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/summary/{order_id}")
async def get_loading_summary(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get loading summary data (for dashboard display).
    """
    # Reuse generate logic but return only summary
    from sqlalchemy.orm import selectinload
    from app.models.order import Order, OrderItem
    from app.models.truck_config import TruckConfig
    
    order_query = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.pipe))
        .where(Order.id == order_id)
    )
    order = (await db.execute(order_query)).scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    length = float(order.pipe_length_m)
    
    # Build order items
    order_items = []
    for item in order.items:
        if item.pipe:
            order_items.append({
                "pipe_id": item.pipe.id,
                "code": item.pipe.code,
                "dn_mm": item.pipe.dn_mm,
                "sdr": item.pipe.sdr,
                "pn_class": item.pipe.pn_class,
                "inner_diameter_mm": float(item.pipe.inner_diameter_mm),
                "wall_mm": float(item.pipe.wall_mm),
                "weight_per_meter": float(item.pipe.weight_per_meter),
                "quantity": item.quantity
            })
    
    if not order_items:
        return {
            "order_id": order_id,
            "total_pipes": 0,
            "total_weight_kg": 0,
            "total_trucks": 0,
            "efficiency_mass_percent": 0,
            "trucks_summary": [],
        }
    
    truck_config = {
        "name": "Standard 24t Romania",
        "max_payload_kg": 24000,
        "internal_length_mm": 13600,
        "internal_width_mm": 2480,
        "internal_height_mm": 2700,
    }
    
    plan = calculate_loading_plan(
        order_items,
        truck_config,
        length,
        enable_nesting=True,
        order_id=order_id
    )
    
    result = loading_plan_to_dict(plan)
    summary = generate_summary_data(result)
    
    return {
        "order_id": order_id,
        "order_number": order.order_number,
        **summary
    }
