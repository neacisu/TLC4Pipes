"""
Unit tests for nesting validator.
"""

import pytest
from app.core.validators.nesting_validator import (
    validate_single_nesting,
    validate_nesting_chain,
    NestingValidationResult,
)


class TestValidateSingleNesting:
    """Tests for single nesting validation."""
    
    def test_valid_nesting(self):
        """Valid nesting passes all checks."""
        host = {
            "code": "TPE630/PN6",
            "dn_mm": 630,
            "inner_diameter_mm": 581.8,
            "sdr": 26,
            "weight_per_meter": 46.64
        }
        guest = {
            "code": "TPE400/PN6",
            "dn_mm": 400,
            "sdr": 26,
            "weight_per_meter": 18.8
        }
        
        result = validate_single_nesting(host, guest, pipe_length_m=12.0)
        
        assert result.is_valid is True
        assert result.gap_check_passed is True
    
    def test_invalid_nesting_gap_too_small(self):
        """Nesting with insufficient gap fails."""
        host = {
            "code": "TPE400/PN6",
            "dn_mm": 400,
            "inner_diameter_mm": 369.4,
            "sdr": 26,
            "weight_per_meter": 18.8
        }
        guest = {
            "code": "TPE355/PN6",
            "dn_mm": 355,
            "sdr": 26,
            "weight_per_meter": 14.79
        }
        
        result = validate_single_nesting(host, guest, pipe_length_m=12.0)
        
        assert result.is_valid is False
        assert result.gap_check_passed is False
    
    def test_sdr_compatibility(self):
        """SDR compatibility is checked."""
        host = {
            "code": "TPE630/PN6",
            "dn_mm": 630,
            "inner_diameter_mm": 581.8,
            "sdr": 26,  # Thin walls
            "weight_per_meter": 46.64
        }
        guest = {
            "code": "TPE400/PN16",
            "dn_mm": 400,
            "sdr": 11,  # Thick walls - heavy
            "weight_per_meter": 42.09
        }
        
        result = validate_single_nesting(host, guest, pipe_length_m=12.0)
        
        # This should warn about heavy guest in light host
        # Validation may still pass geometrically but have warnings


class TestValidateNestingChain:
    """Tests for multi-level nesting validation."""
    
    def test_empty_chain(self):
        """Empty chain is valid but trivial."""
        result = validate_nesting_chain([], pipe_length_m=12.0)
        
        assert result.is_valid is True
        assert result.nesting_levels == 0
    
    def test_single_pipe_chain(self):
        """Single pipe chain is valid."""
        pipes = [{
            "code": "TPE630/PN6",
            "dn_mm": 630,
            "inner_diameter_mm": 581.8,
            "sdr": 26,
            "weight_per_meter": 46.64
        }]
        
        result = validate_nesting_chain(pipes, pipe_length_m=12.0)
        
        assert result.is_valid is True
        assert result.nesting_levels == 1
    
    def test_two_level_valid_chain(self):
        """Two compatible pipes form valid chain."""
        pipes = [
            {
                "code": "TPE630/PN6",
                "dn_mm": 630,
                "inner_diameter_mm": 581.8,
                "sdr": 26,
                "weight_per_meter": 46.64
            },
            {
                "code": "TPE400/PN6",
                "dn_mm": 400,
                "inner_diameter_mm": 369.4,
                "sdr": 26,
                "weight_per_meter": 18.8
            }
        ]
        
        result = validate_nesting_chain(pipes, pipe_length_m=12.0)
        
        assert result.is_valid is True
        assert result.nesting_levels == 2
    
    def test_three_level_chain(self):
        """Three-level nesting works."""
        pipes = [
            {"code": "TPE630/PN6", "dn_mm": 630, "inner_diameter_mm": 581.8, "sdr": 26, "weight_per_meter": 46.64},
            {"code": "TPE400/PN6", "dn_mm": 400, "inner_diameter_mm": 369.4, "sdr": 26, "weight_per_meter": 18.8},
            {"code": "TPE200/PN6", "dn_mm": 200, "inner_diameter_mm": 184.6, "sdr": 26, "weight_per_meter": 4.73},
        ]
        
        result = validate_nesting_chain(pipes, pipe_length_m=12.0)
        
        assert result.is_valid is True
        assert result.nesting_levels == 3
    
    def test_max_levels_exceeded(self):
        """Exceeding max nesting levels triggers warning."""
        # Create a 5-level chain (exceeds default max of 4)
        pipes = [
            {"code": "TPE630/PN6", "dn_mm": 630, "inner_diameter_mm": 581.8, "sdr": 26, "weight_per_meter": 46.64},
            {"code": "TPE400/PN6", "dn_mm": 400, "inner_diameter_mm": 369.4, "sdr": 26, "weight_per_meter": 18.8},
            {"code": "TPE315/PN6", "dn_mm": 315, "inner_diameter_mm": 290.8, "sdr": 26, "weight_per_meter": 11.71},
            {"code": "TPE200/PN6", "dn_mm": 200, "inner_diameter_mm": 184.6, "sdr": 26, "weight_per_meter": 4.73},
            {"code": "TPE110/PN6", "dn_mm": 110, "inner_diameter_mm": 101.6, "sdr": 26, "weight_per_meter": 1.42},
        ]
        
        result = validate_nesting_chain(pipes, pipe_length_m=12.0, max_levels=4)
        
        # Should have warning about max levels
        assert result.nesting_levels == 5
        assert len(result.warnings) > 0 or not result.is_valid
