"""
CSV/Excel Parser for Order Import

Parses order data from CSV or Excel files with pipe specifications.
Supports common formats and delimiters.
"""

import csv
import io
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path


@dataclass
class ParsedOrderItem:
    """Parsed order item from CSV."""
    dn_mm: int
    pn_class: str
    quantity: int
    pipe_code: Optional[str] = None
    row_number: int = 0


@dataclass
class ParseResult:
    """Result of CSV parsing."""
    items: List[ParsedOrderItem]
    errors: List[str]
    warnings: List[str]
    total_rows: int
    valid_rows: int


# Common column name mappings (case-insensitive)
COLUMN_MAPPINGS = {
    # DN / Diameter
    "dn": "dn_mm",
    "dn_mm": "dn_mm",
    "diameter": "dn_mm",
    "diametru": "dn_mm",
    "outer_diameter": "dn_mm",
    "od": "dn_mm",
    
    # PN / Pressure class
    "pn": "pn_class",
    "pn_class": "pn_class",
    "pressure": "pn_class",
    "pressure_class": "pn_class",
    "presiune": "pn_class",
    "clasa_presiune": "pn_class",
    "sdr": "sdr",
    
    # Quantity
    "qty": "quantity",
    "quantity": "quantity",
    "cantitate": "quantity",
    "buc": "quantity",
    "bucati": "quantity",
    "count": "quantity",
    "nr": "quantity",
    
    # Code
    "code": "pipe_code",
    "pipe_code": "pipe_code",
    "cod": "pipe_code",
    "product": "pipe_code",
    "produs": "pipe_code",
}

# SDR to PN mappings
SDR_TO_PN = {
    "26": "PN6",
    "21": "PN8",
    "17": "PN10",
    "11": "PN16",
}


def detect_delimiter(content: str) -> str:
    """
    Detect delimiter used in CSV content.
    
    Args:
        content: CSV file content as string
        
    Returns:
        Detected delimiter character
    """
    # Count occurrences of common delimiters in first few lines
    first_lines = content.split('\n')[:5]
    sample = '\n'.join(first_lines)
    
    delimiters = {
        ',': sample.count(','),
        ';': sample.count(';'),
        '\t': sample.count('\t'),
        '|': sample.count('|'),
    }
    
    # Return delimiter with highest count
    return max(delimiters, key=delimiters.get)


def normalize_column_name(name: str) -> Optional[str]:
    """
    Normalize column name to standard field name.
    
    Args:
        name: Raw column name from CSV header
        
    Returns:
        Normalized field name or None if not recognized
    """
    cleaned = name.strip().lower().replace(' ', '_').replace('-', '_')
    return COLUMN_MAPPINGS.get(cleaned)


def parse_dn_value(value: str) -> Optional[int]:
    """
    Parse DN value from string.
    
    Handles formats like: "200", "DN200", "200mm", "Ø200"
    """
    if not value:
        return None
    
    # Remove common prefixes and suffixes
    cleaned = value.strip().upper()
    for prefix in ['DN', 'Ø', 'D', 'OD']:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    for suffix in ['MM', 'M']:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)]
    
    try:
        return int(float(cleaned.strip()))
    except ValueError:
        return None


def parse_pn_value(value: str) -> Optional[str]:
    """
    Parse PN class from string.
    
    Handles formats like: "PN6", "6", "PN 6", "SDR26"
    """
    if not value:
        return None
    
    cleaned = value.strip().upper()
    
    # Handle SDR format
    if cleaned.startswith('SDR'):
        sdr_value = cleaned[3:].strip()
        return SDR_TO_PN.get(sdr_value)
    
    # Handle PN format
    if cleaned.startswith('PN'):
        cleaned = cleaned[2:].strip()
    
    # Validate PN values
    valid_pn = ['6', '8', '10', '16']
    if cleaned in valid_pn:
        return f"PN{cleaned}"
    
    return None


def parse_quantity(value: str) -> Optional[int]:
    """Parse quantity from string."""
    if not value:
        return None
    
    try:
        qty = int(float(value.strip()))
        return qty if qty > 0 else None
    except ValueError:
        return None


def parse_csv_content(
    content: str,
    delimiter: Optional[str] = None,
    has_header: bool = True
) -> ParseResult:
    """
    Parse CSV content into order items.
    
    Args:
        content: CSV file content as string
        delimiter: CSV delimiter (auto-detected if None)
        has_header: Whether first row is header
        
    Returns:
        ParseResult with parsed items and any errors
    """
    items: List[ParsedOrderItem] = []
    errors: List[str] = []
    warnings: List[str] = []
    
    if not content.strip():
        return ParseResult(
            items=[], errors=["Empty file"], warnings=[],
            total_rows=0, valid_rows=0
        )
    
    # Detect delimiter if not specified
    if delimiter is None:
        delimiter = detect_delimiter(content)
    
    # Parse CSV
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    rows = list(reader)
    
    if not rows:
        return ParseResult(
            items=[], errors=["No data rows found"], warnings=[],
            total_rows=0, valid_rows=0
        )
    
    # Process header
    if has_header:
        header_row = rows[0]
        data_rows = rows[1:]
        
        # Map columns
        column_map: Dict[int, str] = {}
        for idx, col_name in enumerate(header_row):
            normalized = normalize_column_name(col_name)
            if normalized:
                column_map[idx] = normalized
            else:
                warnings.append(f"Unrecognized column: '{col_name}'")
        
        # Check required columns
        mapped_fields = set(column_map.values())
        if 'dn_mm' not in mapped_fields:
            errors.append("Missing required column: DN/Diameter")
        if 'quantity' not in mapped_fields:
            errors.append("Missing required column: Quantity")
        
        if errors:
            return ParseResult(
                items=[], errors=errors, warnings=warnings,
                total_rows=len(data_rows), valid_rows=0
            )
    else:
        # Assume column order: DN, PN, Quantity
        data_rows = rows
        column_map = {0: 'dn_mm', 1: 'pn_class', 2: 'quantity'}
    
    # Parse data rows
    for row_idx, row in enumerate(data_rows, start=2 if has_header else 1):
        if not row or all(not cell.strip() for cell in row):
            continue  # Skip empty rows
        
        row_data: Dict[str, Any] = {}
        for col_idx, field_name in column_map.items():
            if col_idx < len(row):
                row_data[field_name] = row[col_idx]
        
        # Parse values
        dn = parse_dn_value(row_data.get('dn_mm', ''))
        pn = parse_pn_value(row_data.get('pn_class', '') or row_data.get('sdr', ''))
        qty = parse_quantity(row_data.get('quantity', ''))
        code = row_data.get('pipe_code', '').strip() or None
        
        # Validate
        row_errors = []
        if dn is None:
            row_errors.append("Invalid DN value")
        if qty is None:
            row_errors.append("Invalid quantity")
        
        if row_errors:
            errors.append(f"Row {row_idx}: {', '.join(row_errors)}")
            continue
        
        # Default PN if not specified
        if pn is None:
            pn = "PN6"
            warnings.append(f"Row {row_idx}: PN not specified, defaulting to PN6")
        
        # Generate code if not provided
        if code is None:
            code = f"TPE{dn:03d}/{pn}"
        
        items.append(ParsedOrderItem(
            dn_mm=dn,
            pn_class=pn,
            quantity=qty,
            pipe_code=code,
            row_number=row_idx
        ))
    
    return ParseResult(
        items=items,
        errors=errors,
        warnings=warnings,
        total_rows=len(data_rows),
        valid_rows=len(items)
    )


def parse_csv_file(
    file_path: str,
    encoding: str = 'utf-8',
    **kwargs
) -> ParseResult:
    """
    Parse CSV file from path.
    
    Args:
        file_path: Path to CSV file
        encoding: File encoding (default: utf-8)
        **kwargs: Additional arguments for parse_csv_content
        
    Returns:
        ParseResult
    """
    try:
        path = Path(file_path)
        content = path.read_text(encoding=encoding)
        return parse_csv_content(content, **kwargs)
    except FileNotFoundError:
        return ParseResult(
            items=[], errors=[f"File not found: {file_path}"], warnings=[],
            total_rows=0, valid_rows=0
        )
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            content = Path(file_path).read_text(encoding='latin-1')
            return parse_csv_content(content, **kwargs)
        except Exception as e:
            return ParseResult(
                items=[], errors=[f"Encoding error: {str(e)}"], warnings=[],
                total_rows=0, valid_rows=0
            )


def parse_csv_bytes(
    data: bytes,
    **kwargs
) -> ParseResult:
    """
    Parse CSV from bytes (for file upload handling).
    
    Args:
        data: Raw file bytes
        **kwargs: Additional arguments for parse_csv_content
        
    Returns:
        ParseResult
    """
    # Try common encodings
    for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
        try:
            content = data.decode(encoding)
            return parse_csv_content(content, **kwargs)
        except UnicodeDecodeError:
            continue
    
    return ParseResult(
        items=[], errors=["Could not decode file with any supported encoding"],
        warnings=[], total_rows=0, valid_rows=0
    )


def validate_parsed_items(
    items: List[ParsedOrderItem],
    valid_dn_values: Optional[List[int]] = None,
    valid_pn_classes: Optional[List[str]] = None
) -> Tuple[List[ParsedOrderItem], List[str]]:
    """
    Validate parsed items against catalog.
    
    Args:
        items: Parsed order items
        valid_dn_values: List of valid DN values (from pipe catalog)
        valid_pn_classes: List of valid PN classes
        
    Returns:
        Tuple of (valid_items, error_messages)
    """
    valid_items = []
    errors = []
    
    valid_dn = set(valid_dn_values or [
        20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160,
        180, 200, 225, 250, 280, 315, 355, 400, 450, 500,
        560, 630, 710, 800
    ])
    valid_pn = set(valid_pn_classes or ['PN6', 'PN8', 'PN10', 'PN16'])
    
    for item in items:
        if item.dn_mm not in valid_dn:
            errors.append(
                f"Row {item.row_number}: DN{item.dn_mm} not in catalog"
            )
            continue
        
        if item.pn_class not in valid_pn:
            errors.append(
                f"Row {item.row_number}: {item.pn_class} not valid"
            )
            continue
        
        valid_items.append(item)
    
    return valid_items, errors
