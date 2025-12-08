"""
Unit tests for nesting algorithm.
"""

import pytest
from app.core.algorithms.nesting import (
    NestedPipe,
    create_nested_bundles,
    bundle_to_dict,
    MAX_NESTING_LEVELS
)


class TestNestedPipe:
    """Tests for NestedPipe dataclass."""
    
    def test_single_pipe_bundle(self):
        """Single pipe bundle has nesting level 1."""
        pipe = NestedPipe(
            pipe_data={"code": "TPE400", "weight_per_meter": 18.8}
        )
        
        assert pipe.total_nesting_levels == 1
        assert len(pipe.get_all_pipes()) == 1
    
    def test_two_level_nesting(self):
        """Two-level nesting has correct depth."""
        outer = NestedPipe(
            pipe_data={"code": "TPE630", "weight_per_meter": 46.64}
        )
        inner = NestedPipe(
            pipe_data={"code": "TPE400", "weight_per_meter": 18.8}
        )
        outer.nested_pipes.append(inner)
        
        assert outer.total_nesting_levels == 2
        assert len(outer.get_all_pipes()) == 2
    
    def test_bundle_weight_calculation(self):
        """Bundle weight should sum all nested pipes."""
        outer = NestedPipe(
            pipe_data={"code": "TPE630", "weight_per_meter": 46.64}
        )
        inner = NestedPipe(
            pipe_data={"code": "TPE400", "weight_per_meter": 18.8}
        )
        outer.nested_pipes.append(inner)
        
        # At 12m length
        expected_weight = (46.64 + 18.8) * 12
        assert outer.calculate_bundle_weight(12.0) == pytest.approx(expected_weight, 0.1)


class TestCreateNestedBundles:
    """Tests for bundle creation algorithm."""
    
    def test_empty_input(self):
        """Empty input returns empty result."""
        result = create_nested_bundles([])
        
        assert result.bundles == []
        assert result.total_pipes_processed == 0
    
    def test_single_pipe(self):
        """Single pipe creates single bundle."""
        pipes = [{"code": "TPE400", "dn_mm": 400, "weight_per_meter": 18.8}]
        
        result = create_nested_bundles(pipes)
        
        assert len(result.bundles) == 1
        assert result.total_pipes_processed == 1
    
    def test_compatible_pipes_nest(self):
        """Compatible pipes should be nested together."""
        pipes = [
            {"code": "TPE630", "dn_mm": 630, "inner_diameter_mm": 581.8, "weight_per_meter": 46.64},
            {"code": "TPE400", "dn_mm": 400, "inner_diameter_mm": 369.4, "weight_per_meter": 18.8},
        ]
        
        result = create_nested_bundles(pipes)
        
        # Should create 1 bundle with nesting
        assert len(result.bundles) == 1
        assert result.pipes_nested >= 1  # At least one pipe nested


class TestBundleToDict:
    """Tests for bundle serialization."""
    
    def test_serialization(self):
        """Bundle should serialize to dict with all fields."""
        outer = NestedPipe(
            pipe_data={"code": "TPE630", "dn_mm": 630, "weight_per_meter": 46.64}
        )
        
        result = bundle_to_dict(outer, 12.0)
        
        assert "outer_pipe" in result
        assert "nested_pipes" in result
        assert "nesting_levels" in result
        assert "bundle_weight_kg" in result
        assert result["outer_pipe"]["code"] == "TPE630"
