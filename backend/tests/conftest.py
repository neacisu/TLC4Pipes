"""
Pytest configuration and fixtures.
"""

import pytest


@pytest.fixture
def sample_pipes():
    """Sample pipe data for testing."""
    return [
        {"code": "TPE800/PN6", "dn_mm": 800, "inner_diameter_mm": 738.8, "sdr": 26, "pn_class": "PN6", "weight_per_meter": 75.19},
        {"code": "TPE630/PN6", "dn_mm": 630, "inner_diameter_mm": 581.8, "sdr": 26, "pn_class": "PN6", "weight_per_meter": 46.64},
        {"code": "TPE500/PN6", "dn_mm": 500, "inner_diameter_mm": 461.8, "sdr": 26, "pn_class": "PN6", "weight_per_meter": 29.34},
        {"code": "TPE400/PN6", "dn_mm": 400, "inner_diameter_mm": 369.4, "sdr": 26, "pn_class": "PN6", "weight_per_meter": 18.80},
        {"code": "TPE315/PN6", "dn_mm": 315, "inner_diameter_mm": 290.8, "sdr": 26, "pn_class": "PN6", "weight_per_meter": 11.71},
        {"code": "TPE200/PN6", "dn_mm": 200, "inner_diameter_mm": 184.6, "sdr": 26, "pn_class": "PN6", "weight_per_meter": 4.73},
        {"code": "TPE110/PN6", "dn_mm": 110, "inner_diameter_mm": 101.6, "sdr": 26, "pn_class": "PN6", "weight_per_meter": 1.42},
    ]


@pytest.fixture
def sample_truck_config():
    """Sample truck configuration."""
    return {
        "name": "Standard 24t Romania",
        "max_payload_kg": 24000,
        "internal_length_mm": 13600,
        "internal_width_mm": 2480,
        "internal_height_mm": 2700,
        "max_axle_weight_kg": 11500
    }


@pytest.fixture
def sample_order_items():
    """Sample order items for testing."""
    return [
        {"pipe_id": 1, "code": "TPE630/PN6", "dn_mm": 630, "inner_diameter_mm": 581.8, "weight_per_meter": 46.64, "quantity": 5},
        {"pipe_id": 2, "code": "TPE400/PN6", "dn_mm": 400, "inner_diameter_mm": 369.4, "weight_per_meter": 18.80, "quantity": 10},
        {"pipe_id": 3, "code": "TPE110/PN6", "dn_mm": 110, "inner_diameter_mm": 101.6, "weight_per_meter": 1.42, "quantity": 20},
    ]
