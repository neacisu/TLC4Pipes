"""
Physical Constants and Configuration Values

Constants from the HDPE pipe loading specification document.
"""

# HDPE Material Properties
HDPE_DENSITY_KG_M3 = 950  # kg/m³ - Standard PE100 density
HDPE_FRICTION_COEFFICIENT = 0.25  # HDPE on HDPE friction (0.2-0.3 range)

# SDR (Standard Dimension Ratio) Mappings
SDR_TO_PN = {
    26: "PN6",
    21: "PN8", 
    17: "PN10",
    11: "PN16",
}

PN_TO_SDR = {v: k for k, v in SDR_TO_PN.items()}

# Available SDR values (sorted by wall thickness, thinnest first)
AVAILABLE_SDRS = [26, 21, 17, 11]

# Available pipe lengths in meters
AVAILABLE_PIPE_LENGTHS_M = [12.0, 12.5, 13.0]
DEFAULT_PIPE_LENGTH_M = 12.0

# Gap Clearance Constants (from specification section 3.1)
BASE_CLEARANCE_MM = 15.0  # Minimum absolute gap for handling
DIAMETER_FACTOR = 0.015   # 1.5% of outer diameter for ovality
OVALITY_FACTOR = 0.04     # 4% max ovality during transport

# Nesting Limits (from specification section 3.3)
MAX_NESTING_LEVELS = 10
HEAVY_EXTRACTION_THRESHOLD_KG = 2000  # Warn if bundle > 2000kg

# Transport Limits - Romania (from OG 43/1997, CNAIR norms)
MAX_PAYLOAD_KG = 24000            # Maximum cargo weight
MAX_TOTAL_VEHICLE_KG = 40000      # Total vehicle + cargo
MAX_AXLE_WEIGHT_MOTOR_KG = 11500  # Tractor motor axle
MAX_AXLE_WEIGHT_TRAILER_KG = 8000 # Per trailer axle (3 axles total)

# Optimal Center of Gravity Range (from trailer front, in meters)
OPTIMAL_COG_MIN_M = 5.5
OPTIMAL_COG_MAX_M = 7.5

# Standard Truck Dimensions (mm)
STANDARD_TRUCK_LENGTH_MM = 13600
STANDARD_TRUCK_WIDTH_MM = 2480
STANDARD_TRUCK_HEIGHT_MM = 2700
MEGA_TRUCK_HEIGHT_MM = 3000

# Kingpin position from front of trailer (for axle calculations)
KINGPIN_POSITION_M = 1.5

# Safety Margins
WEIGHT_SAFETY_MARGIN_PERCENT = 2.0  # 2% safety margin on weight
GAP_SAFETY_MARGIN_MM = 5.0  # Additional gap safety

# Packing Efficiency Constants
SQUARE_PACKING_EFFICIENCY = 0.785  # π/4 ≈ 78.5%
HEXAGONAL_PACKING_EFFICIENCY = 0.907  # ≈ 90.7%

# Strapping/Securing Recommendations
RECOMMENDED_STRAP_FORCE_DAN = 500  # Standard strap pretension
STRAPS_PER_TONNE = 0.5  # Approximately 1 strap per 2 tonnes

# Pipe Diameter Ranges
MIN_PIPE_DN_MM = 20
MAX_PIPE_DN_MM = 1200

# Common diameter steps (DN values in mm)
STANDARD_DN_VALUES = [
    20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 
    180, 200, 225, 250, 280, 315, 355, 400, 450, 500, 
    560, 630, 710, 800, 900, 1000, 1200
]
