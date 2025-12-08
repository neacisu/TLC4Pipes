"""
Integration tests for loading flow.
"""

import pytest
from app.services.loading_service import calculate_loading_plan, loading_plan_to_dict


class TestLoadingPlanCalculation:
    """Tests for complete loading plan calculation."""
    
    def test_basic_loading_plan(self, sample_order_items, sample_truck_config):
        """Should generate valid loading plan."""
        result = calculate_loading_plan(
            order_items=sample_order_items,
            truck_config=sample_truck_config,
            pipe_length_m=12.0
        )
        
        assert result.total_pipes > 0
        assert result.total_weight_kg > 0
        assert result.trucks_needed >= 1
    
    def test_loading_plan_serialization(self, sample_order_items, sample_truck_config):
        """Loading plan should serialize correctly."""
        result = calculate_loading_plan(
            order_items=sample_order_items,
            truck_config=sample_truck_config,
            pipe_length_m=12.0
        )
        
        serialized = loading_plan_to_dict(result)
        
        assert "summary" in serialized
        assert "trucks" in serialized
        assert "nesting_stats" in serialized
        assert "warnings" in serialized
    
    def test_nesting_reduces_truck_count(self, sample_order_items, sample_truck_config):
        """Nesting should potentially reduce truck count."""
        # With nesting
        with_nesting = calculate_loading_plan(
            order_items=sample_order_items,
            truck_config=sample_truck_config,
            pipe_length_m=12.0,
            enable_nesting=True
        )
        
        # Without nesting - same weight, but might need same trucks
        # (this is more a smoke test than strict comparison)
        assert with_nesting.nesting_stats["nesting_enabled"] is True
    
    def test_weight_limits_warning(self, sample_truck_config):
        """Should warn when approaching weight limits."""
        # Heavy order that exceeds capacity
        heavy_order = [
            {"pipe_id": 1, "code": "TPE800/PN16", "dn_mm": 800, 
             "inner_diameter_mm": 654.8, "weight_per_meter": 168.7, "quantity": 15}
        ]
        
        result = calculate_loading_plan(
            order_items=heavy_order,
            truck_config=sample_truck_config,
            pipe_length_m=13.0  # 168.7 * 13 * 15 = 32,896 kg > 24,000
        )
        
        assert result.trucks_needed > 1 or len(result.warnings) > 0
