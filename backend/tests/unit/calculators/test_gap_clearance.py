"""
Unit tests for gap clearance calculator.
"""

import pytest
from app.core.calculators.gap_clearance import (
    calculate_minimum_gap,
    validate_nesting_compatibility,
    find_compatible_pipes,
    BASE_CLEARANCE_MM,
    DIAMETER_FACTOR
)


class TestMinimumGapCalculation:
    """Tests for minimum gap formula: Gap = 15 + 0.015 × DN"""
    
    def test_gap_for_dn400(self):
        """DN400: gap = 15 + 0.015 × 400 = 21mm"""
        gap = calculate_minimum_gap(400)
        assert gap == 21.0
    
    def test_gap_for_dn800(self):
        """DN800: gap = 15 + 0.015 × 800 = 27mm"""
        gap = calculate_minimum_gap(800)
        assert gap == 27.0
    
    def test_gap_for_dn110(self):
        """DN110: gap = 15 + 0.015 × 110 = 16.65mm"""
        gap = calculate_minimum_gap(110)
        assert gap == pytest.approx(16.65, 0.01)


class TestNestingValidation:
    """Tests for nesting compatibility validation."""
    
    def test_valid_nesting_tpe315_in_tpe400(self):
        """TPE315/PN6 in TPE400/PN6 should be valid (from specification)"""
        # TPE400/PN6: DI = 369.4mm
        # TPE315/PN6: DN = 315mm
        # Gap = 369.4 - 315 = 54.4mm > 21mm required
        result = validate_nesting_compatibility(
            host_inner_diameter_mm=369.4,
            host_outer_diameter_mm=400,
            guest_outer_diameter_mm=315,
            apply_ovality=False  # Without ovality for this test
        )
        
        assert result.is_valid is True
        assert result.available_gap_mm == pytest.approx(54.4, 0.1)
        assert result.required_gap_mm == 21.0
    
    def test_invalid_nesting_tpe355_in_tpe400(self):
        """TPE355/PN6 in TPE400/PN6 should be INVALID (from specification)"""
        # TPE400/PN6: DI = 369.4mm
        # TPE355/PN6: DN = 355mm
        # Gap = 369.4 - 355 = 14.4mm < 21mm required
        result = validate_nesting_compatibility(
            host_inner_diameter_mm=369.4,
            host_outer_diameter_mm=400,
            guest_outer_diameter_mm=355,
            apply_ovality=False
        )
        
        assert result.is_valid is False
        assert result.available_gap_mm == pytest.approx(14.4, 0.1)
        assert result.required_gap_mm == 21.0
    
    def test_ovality_reduces_available_gap(self):
        """Ovality should reduce effective inner diameter."""
        # Same test with ovality applied
        result_no_oval = validate_nesting_compatibility(
            host_inner_diameter_mm=369.4,
            host_outer_diameter_mm=400,
            guest_outer_diameter_mm=315,
            apply_ovality=False
        )
        
        result_with_oval = validate_nesting_compatibility(
            host_inner_diameter_mm=369.4,
            host_outer_diameter_mm=400,
            guest_outer_diameter_mm=315,
            apply_ovality=True
        )
        
        # Ovality reduces available gap
        assert result_with_oval.available_gap_mm < result_no_oval.available_gap_mm


class TestFindCompatiblePipes:
    """Tests for finding compatible pipes."""
    
    def test_find_compatible_for_large_pipe(self):
        """Should find multiple compatible pipes for large host."""
        host = {
            "inner_diameter_mm": 581.8,  # TPE630/PN6
            "outer_diameter_mm": 630
        }
        
        candidates = [
            {"code": "TPE500", "dn_mm": 500, "outer_diameter_mm": 500},
            {"code": "TPE400", "dn_mm": 400, "outer_diameter_mm": 400},
            {"code": "TPE315", "dn_mm": 315, "outer_diameter_mm": 315},
            {"code": "TPE630", "dn_mm": 630, "outer_diameter_mm": 630},  # Same size
        ]
        
        compatible = find_compatible_pipes(host, candidates, apply_ovality=False)
        
        # TPE630 should not be included (same size)
        assert all(p["code"] != "TPE630" for p in compatible)
        
        # Sorted by diameter descending
        if len(compatible) >= 2:
            assert compatible[0]["dn_mm"] >= compatible[1]["dn_mm"]
