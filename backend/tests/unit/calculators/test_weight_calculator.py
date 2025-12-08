"""
Unit tests for weight calculator.
"""

import pytest
from app.core.calculators.weight_calculator import (
    calculate_pipe_weight,
    calculate_bundle_weight,
    check_weight_limits,
    HEAVY_EXTRACTION_THRESHOLD_KG,
)


class TestPipeWeight:
    """Tests for single pipe weight calculation."""
    
    def test_basic_weight_calculation(self):
        """Basic weight = weight_per_meter × length × quantity."""
        result = calculate_pipe_weight(
            weight_per_meter=10.0,
            length_m=12.0,
            quantity=1
        )
        
        assert result.total_weight_kg == 120.0
        assert result.single_pipe_weight_kg == 120.0
    
    def test_multiple_pipes(self):
        """Multiple pipes multiply weight."""
        result = calculate_pipe_weight(
            weight_per_meter=10.0,
            length_m=12.0,
            quantity=5
        )
        
        assert result.total_weight_kg == 600.0  # 10 * 12 * 5
        assert result.single_pipe_weight_kg == 120.0  # 10 * 12
    
    def test_real_pipe_data(self):
        """Test with real TPE630/PN6 data."""
        # TPE630/PN6: 46.64 kg/m
        result = calculate_pipe_weight(
            weight_per_meter=46.64,
            length_m=12.0,
            quantity=3
        )
        
        single_expected = 46.64 * 12
        total_expected = single_expected * 3
        
        assert result.single_pipe_weight_kg == pytest.approx(single_expected, 0.1)
        assert result.total_weight_kg == pytest.approx(total_expected, 0.1)
    
    def test_heavy_pipe_warning(self):
        """Heavy pipes trigger warning."""
        # TPE800/PN16: 168.7 kg/m, 12m = 2024 kg (> 2000 threshold)
        result = calculate_pipe_weight(
            weight_per_meter=168.7,
            length_m=12.0,
            quantity=1
        )
        
        assert result.single_pipe_weight_kg > HEAVY_EXTRACTION_THRESHOLD_KG
        assert result.requires_heavy_equipment is True


class TestBundleWeight:
    """Tests for nested bundle weight calculation."""
    
    def test_single_pipe_bundle(self):
        """Bundle with single pipe."""
        pipes = [{"weight_per_meter": 18.8}]  # DN400
        
        result = calculate_bundle_weight(pipes, length_m=12.0)
        
        assert result == pytest.approx(18.8 * 12, 0.1)
    
    def test_nested_bundle(self):
        """Bundle with nested pipes sums weights."""
        pipes = [
            {"weight_per_meter": 46.64},  # DN630
            {"weight_per_meter": 18.8},   # DN400 (nested)
            {"weight_per_meter": 1.42},   # DN110 (nested)
        ]
        
        result = calculate_bundle_weight(pipes, length_m=12.0)
        
        expected = (46.64 + 18.8 + 1.42) * 12
        assert result == pytest.approx(expected, 0.1)
    
    def test_empty_bundle(self):
        """Empty pipe list returns zero."""
        result = calculate_bundle_weight([], length_m=12.0)
        assert result == 0.0


class TestWeightLimits:
    """Tests for weight limit checking."""
    
    def test_under_limit(self):
        """Weight under limit passes."""
        result = check_weight_limits(
            total_weight_kg=20000,
            max_weight_kg=24000
        )
        
        assert result.is_valid is True
        assert result.utilization_percent == pytest.approx(83.33, 0.1)
    
    def test_at_limit(self):
        """Weight exactly at limit passes."""
        result = check_weight_limits(
            total_weight_kg=24000,
            max_weight_kg=24000
        )
        
        assert result.is_valid is True
        assert result.utilization_percent == 100.0
    
    def test_over_limit(self):
        """Weight over limit fails."""
        result = check_weight_limits(
            total_weight_kg=25000,
            max_weight_kg=24000
        )
        
        assert result.is_valid is False
        assert result.excess_kg == 1000
    
    def test_high_utilization_warning(self):
        """High utilization (>95%) triggers warning."""
        result = check_weight_limits(
            total_weight_kg=23500,
            max_weight_kg=24000
        )
        
        assert result.is_valid is True
        assert result.utilization_percent > 95
        # Should have a warning about high utilization
