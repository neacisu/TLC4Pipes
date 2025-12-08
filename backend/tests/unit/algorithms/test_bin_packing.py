"""
Unit tests for bin packing algorithm.
"""

import pytest
from app.core.algorithms.bin_packing import (
    first_fit_decreasing,
    pack_pipes_into_trucks,
    TruckLoad,
    PackingResult,
)


class TestFirstFitDecreasing:
    """Tests for FFD algorithm."""
    
    def test_empty_bundles(self):
        """Empty bundles returns empty result."""
        truck_config = {"max_payload_kg": 24000}
        result = first_fit_decreasing([], truck_config, pipe_length_m=12.0)
        
        assert result.total_trucks_needed == 0
        assert result.total_weight_kg == 0
        assert result.trucks == []
    
    def test_single_light_bundle(self):
        """Single light bundle fits in one truck."""
        from app.core.algorithms.nesting import NestedPipe
        
        bundle = NestedPipe(
            pipe_data={"code": "TPE110/PN6", "dn_mm": 110, "weight_per_meter": 1.42}
        )
        
        truck_config = {"max_payload_kg": 24000}
        result = first_fit_decreasing([bundle], truck_config, pipe_length_m=12.0)
        
        assert result.total_trucks_needed == 1
        assert result.total_weight_kg == pytest.approx(1.42 * 12, 0.1)
    
    def test_multiple_bundles_single_truck(self):
        """Multiple light bundles fit in one truck."""
        from app.core.algorithms.nesting import NestedPipe
        
        bundles = [
            NestedPipe(pipe_data={"code": f"TPE110/PN6_{i}", "dn_mm": 110, "weight_per_meter": 1.42})
            for i in range(10)
        ]
        
        truck_config = {"max_payload_kg": 24000}
        result = first_fit_decreasing(bundles, truck_config, pipe_length_m=12.0)
        
        assert result.total_trucks_needed == 1
        expected_weight = 10 * 1.42 * 12
        assert result.total_weight_kg == pytest.approx(expected_weight, 0.1)
    
    def test_heavy_bundles_multiple_trucks(self):
        """Heavy bundles require multiple trucks."""
        from app.core.algorithms.nesting import NestedPipe
        
        # Create bundles that exceed single truck capacity
        # TPE800/PN16: 168.7 kg/m * 12m = 2024 kg per pipe
        # Need ~12 to exceed 24000 kg
        bundles = [
            NestedPipe(pipe_data={"code": f"TPE800/PN16_{i}", "dn_mm": 800, "weight_per_meter": 168.7})
            for i in range(15)
        ]
        
        truck_config = {"max_payload_kg": 24000}
        result = first_fit_decreasing(bundles, truck_config, pipe_length_m=12.0)
        
        assert result.total_trucks_needed >= 2
        total_expected = 15 * 168.7 * 12
        assert result.total_weight_kg == pytest.approx(total_expected, 10)
    
    def test_descending_weight_order(self):
        """Bundles should be sorted by weight descending."""
        from app.core.algorithms.nesting import NestedPipe
        
        bundles = [
            NestedPipe(pipe_data={"code": "LIGHT", "dn_mm": 110, "weight_per_meter": 1.42}),
            NestedPipe(pipe_data={"code": "HEAVY", "dn_mm": 800, "weight_per_meter": 168.7}),
            NestedPipe(pipe_data={"code": "MEDIUM", "dn_mm": 315, "weight_per_meter": 11.71}),
        ]
        
        truck_config = {"max_payload_kg": 24000}
        result = first_fit_decreasing(bundles, truck_config, pipe_length_m=12.0)
        
        # All should fit in one truck
        assert result.total_trucks_needed == 1
        
        # First bundle in truck should be heaviest
        if result.trucks[0].bundles:
            first_bundle = result.trucks[0].bundles[0]
            assert first_bundle.pipe_data.get("code") == "HEAVY"


class TestTruckLoad:
    """Tests for TruckLoad dataclass."""
    
    def test_empty_truck(self):
        """Empty truck has zero weight and utilization."""
        truck = TruckLoad(truck_number=1, max_payload_kg=24000)
        
        assert truck.total_weight_kg == 0
        assert truck.utilization_percent == 0
        assert truck.remaining_capacity_kg == 24000
    
    def test_add_bundle(self):
        """Adding bundle updates weight correctly."""
        from app.core.algorithms.nesting import NestedPipe
        
        truck = TruckLoad(truck_number=1, max_payload_kg=24000)
        bundle = NestedPipe(
            pipe_data={"code": "TPE400", "weight_per_meter": 18.8}
        )
        
        can_fit = truck.can_fit(bundle, 12.0)
        assert can_fit is True
        
        truck.add_bundle(bundle, 12.0)
        
        expected_weight = 18.8 * 12
        assert truck.total_weight_kg == pytest.approx(expected_weight, 0.1)
        assert truck.remaining_capacity_kg == pytest.approx(24000 - expected_weight, 0.1)
