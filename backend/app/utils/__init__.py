"""
Utilities Module

Common utilities for constants, conversions, and data parsing.
"""

from app.utils.constants import (
    # Material properties
    HDPE_DENSITY_KG_M3,
    HDPE_FRICTION_COEFFICIENT,
    # SDR mappings
    SDR_TO_PN,
    PN_TO_SDR,
    AVAILABLE_SDRS,
    # Pipe lengths
    AVAILABLE_PIPE_LENGTHS_M,
    DEFAULT_PIPE_LENGTH_M,
    # Gap clearance
    BASE_CLEARANCE_MM,
    DIAMETER_FACTOR,
    OVALITY_FACTOR,
    # Nesting limits
    MAX_NESTING_LEVELS,
    HEAVY_EXTRACTION_THRESHOLD_KG,
    # Transport limits
    MAX_PAYLOAD_KG,
    MAX_AXLE_WEIGHT_MOTOR_KG,
    MAX_AXLE_WEIGHT_TRAILER_KG,
    OPTIMAL_COG_MIN_M,
    OPTIMAL_COG_MAX_M,
)
from app.utils.converters import (
    mm_to_m,
    m_to_mm,
    kg_to_tonnes,
    tonnes_to_kg,
    calculate_pipe_weight_kg,
    calculate_hexagonal_stack_height_mm,
    calculate_max_hexagonal_rows,
    format_weight_kg,
    format_dimension_mm,
)
from app.utils.csv_parser import (
    parse_csv_content,
    parse_csv_file,
    parse_csv_bytes,
    validate_parsed_items,
    ParsedOrderItem,
    ParseResult,
)

__all__ = [
    # Constants
    "HDPE_DENSITY_KG_M3",
    "HDPE_FRICTION_COEFFICIENT",
    "SDR_TO_PN",
    "PN_TO_SDR",
    "AVAILABLE_SDRS",
    "AVAILABLE_PIPE_LENGTHS_M",
    "DEFAULT_PIPE_LENGTH_M",
    "BASE_CLEARANCE_MM",
    "DIAMETER_FACTOR",
    "OVALITY_FACTOR",
    "MAX_NESTING_LEVELS",
    "HEAVY_EXTRACTION_THRESHOLD_KG",
    "MAX_PAYLOAD_KG",
    "MAX_AXLE_WEIGHT_MOTOR_KG",
    "MAX_AXLE_WEIGHT_TRAILER_KG",
    "OPTIMAL_COG_MIN_M",
    "OPTIMAL_COG_MAX_M",
    # Converters
    "mm_to_m",
    "m_to_mm",
    "kg_to_tonnes",
    "tonnes_to_kg",
    "calculate_pipe_weight_kg",
    "calculate_hexagonal_stack_height_mm",
    "calculate_max_hexagonal_rows",
    "format_weight_kg",
    "format_dimension_mm",
    # CSV parser
    "parse_csv_content",
    "parse_csv_file",
    "parse_csv_bytes",
    "validate_parsed_items",
    "ParsedOrderItem",
    "ParseResult",
]
