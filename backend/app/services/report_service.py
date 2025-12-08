"""
Report Service

PDF report generation for loading plans.
Uses ReportLab for PDF creation.
"""

import io
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

# Check if reportlab is available
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, PageBreak, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


@dataclass
class LoadingReportData:
    """Data for loading report generation."""
    order_number: str
    pipe_length_m: float
    total_pipes: int
    total_weight_kg: float
    trucks: List[dict]
    nesting_stats: dict
    generated_at: datetime


def generate_loading_report_pdf(
    report_data: LoadingReportData,
    include_instructions: bool = True
) -> bytes:
    """
    Generate PDF loading report.
    
    Args:
        report_data: Report data
        include_instructions: Include loading instructions
        
    Returns:
        PDF file as bytes
    """
    if not REPORTLAB_AVAILABLE:
        return generate_simple_text_report(report_data).encode('utf-8')
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8
    )
    normal_style = styles['Normal']
    
    elements = []
    
    # Title
    elements.append(Paragraph(
        "PLAN DE ÎNCĂRCARE - ȚEVI HDPE",
        title_style
    ))
    elements.append(Spacer(1, 12))
    
    # Order info
    elements.append(Paragraph(f"<b>Comandă:</b> {report_data.order_number}", normal_style))
    elements.append(Paragraph(f"<b>Data:</b> {report_data.generated_at.strftime('%d.%m.%Y %H:%M')}", normal_style))
    elements.append(Paragraph(f"<b>Lungime țevi:</b> {report_data.pipe_length_m} m", normal_style))
    elements.append(Spacer(1, 12))
    
    # Summary
    elements.append(Paragraph("Rezumat", heading_style))
    
    summary_data = [
        ["Total țevi", str(report_data.total_pipes)],
        ["Greutate totală", f"{report_data.total_weight_kg:,.0f} kg"],
        ["Camioane necesare", str(len(report_data.trucks))],
        ["Pachete telescopate", str(report_data.nesting_stats.get('bundles_with_nesting', 0))],
    ]
    
    summary_table = Table(summary_data, colWidths=[6*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Truck details
    for truck in report_data.trucks:
        truck_num = truck.get('truck_number', 1)
        elements.append(Paragraph(f"Camion {truck_num}", heading_style))
        
        truck_info = [
            ["Greutate încărcată", f"{truck.get('total_weight_kg', 0):,.0f} kg"],
            ["Grad utilizare", f"{truck.get('weight_utilization_pct', 0):.1f}%"],
            ["Pachete", str(truck.get('bundle_count', 0))],
        ]
        
        truck_table = Table(truck_info, colWidths=[5*cm, 3*cm])
        truck_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(truck_table)
        elements.append(Spacer(1, 8))
        
        # Bundle list
        bundles = truck.get('bundles', [])
        if bundles:
            bundle_data = [['#', 'Țeavă exterioară', 'Țevi incluse', 'Greutate']]
            
            for i, bundle in enumerate(bundles, 1):
                outer = bundle.get('outer_pipe', {})
                nested_count = bundle.get('total_pipes', 1) - 1
                weight = bundle.get('bundle_weight_kg', 0)
                
                bundle_data.append([
                    str(i),
                    outer.get('code', 'N/A'),
                    f"+{nested_count}" if nested_count > 0 else "-",
                    f"{weight:.0f} kg"
                ])
            
            bundle_table = Table(bundle_data, colWidths=[1*cm, 5*cm, 3*cm, 3*cm])
            bundle_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(bundle_table)
        
        elements.append(Spacer(1, 15))
    
    # Loading instructions
    if include_instructions:
        elements.append(Paragraph("Instrucțiuni de Încărcare", heading_style))
        
        instructions = generate_loading_instructions(report_data)
        for instruction in instructions:
            elements.append(Paragraph(f"• {instruction}", normal_style))
        
        elements.append(Spacer(1, 12))
    
    # Safety notes
    elements.append(Paragraph("Note de Siguranță", heading_style))
    safety_notes = [
        "Verificați integritatea tuturor pachetelor înainte de încărcare",
        "Utilizați chingi de ancorare corespunzătoare (min. STF 500daN)",
        "Poziționați pachetele grele central pentru echilibru",
        "Nu depășiți înălțimea maximă a semiremorcii",
    ]
    for note in safety_notes:
        elements.append(Paragraph(f"⚠ {note}", normal_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.read()


def generate_simple_text_report(report_data: LoadingReportData) -> str:
    """
    Generate simple text report (fallback when ReportLab not available).
    
    Args:
        report_data: Report data
        
    Returns:
        Text report
    """
    lines = [
        "=" * 50,
        "PLAN DE ÎNCĂRCARE - ȚEVI HDPE",
        "=" * 50,
        "",
        f"Comandă: {report_data.order_number}",
        f"Data: {report_data.generated_at.strftime('%d.%m.%Y %H:%M')}",
        f"Lungime țevi: {report_data.pipe_length_m} m",
        "",
        "-" * 50,
        "REZUMAT",
        "-" * 50,
        f"Total țevi: {report_data.total_pipes}",
        f"Greutate totală: {report_data.total_weight_kg:,.0f} kg",
        f"Camioane necesare: {len(report_data.trucks)}",
        "",
    ]
    
    for truck in report_data.trucks:
        lines.append("-" * 50)
        lines.append(f"CAMION {truck.get('truck_number', 1)}")
        lines.append("-" * 50)
        lines.append(f"Greutate: {truck.get('total_weight_kg', 0):,.0f} kg")
        lines.append(f"Utilizare: {truck.get('weight_utilization_pct', 0):.1f}%")
        lines.append("")
        
        for bundle in truck.get('bundles', []):
            outer = bundle.get('outer_pipe', {})
            lines.append(f"  - {outer.get('code', 'N/A')}: {bundle.get('bundle_weight_kg', 0):.0f} kg")
        
        lines.append("")
    
    return "\n".join(lines)


def generate_loading_instructions(report_data: LoadingReportData) -> List[str]:
    """
    Generate step-by-step loading instructions.
    
    Args:
        report_data: Report data
        
    Returns:
        List of instruction strings
    """
    instructions = []
    
    for truck in report_data.trucks:
        truck_num = truck.get('truck_number', 1)
        bundles = truck.get('bundles', [])
        
        if not bundles:
            continue
        
        instructions.append(f"Camion {truck_num}:")
        
        # Group bundles by type
        nested_bundles = [b for b in bundles if b.get('total_pipes', 1) > 1]
        single_pipes = [b for b in bundles if b.get('total_pipes', 1) == 1]
        
        if nested_bundles:
            instructions.append(f"  Pregătiți {len(nested_bundles)} pachete telescopate")
            for i, bundle in enumerate(nested_bundles, 1):
                outer = bundle.get('outer_pipe', {})
                nested = bundle.get('nested_pipes', [])
                if nested:
                    inner_codes = [n.get('outer_pipe', {}).get('code', '?') for n in nested]
                    instructions.append(
                        f"    Pachet {i}: {outer.get('code')} conține: {', '.join(inner_codes)}"
                    )
        
        if single_pipes:
            instructions.append(f"  Încărcați {len(single_pipes)} țevi individuale")
        
        # Heavy extraction warning
        heavy = [b for b in bundles if b.get('requires_heavy_extraction', False)]
        if heavy:
            instructions.append(
                f"  ⚠ {len(heavy)} pachete necesită utilaj greu pentru descărcare"
            )
    
    return instructions


def generate_summary_data(loading_plan: dict) -> dict:
    """
    Generate summary data for dashboard display.
    
    Args:
        loading_plan: Loading plan result dict
        
    Returns:
        Summary dict for frontend
    """
    trucks = loading_plan.get('trucks', [])
    summary = loading_plan.get('summary', {})
    
    return {
        'total_pipes': summary.get('total_pipes', 0),
        'total_weight_kg': summary.get('total_weight_kg', 0),
        'total_trucks': len(trucks),
        'trucks_summary': [
            {
                'truck_number': t.get('truck_number'),
                'weight_kg': t.get('total_weight_kg', 0),
                'utilization_pct': t.get('weight_utilization_pct', 0),
                'bundle_count': t.get('bundle_count', 0),
            }
            for t in trucks
        ],
        'efficiency': {
            'mass_pct': sum(t.get('weight_utilization_pct', 0) for t in trucks) / len(trucks) if trucks else 0,
            'nesting_enabled': loading_plan.get('nesting_stats', {}).get('nesting_enabled', False),
            'bundles_nested': loading_plan.get('nesting_stats', {}).get('bundles_with_nesting', 0),
        }
    }
