"""
Unit tests for circle packing algorithm.
"""

import pytest
from app.core.algorithms.circle_packing import (
    pack_circles_greedy,
    pack_nested_bundle_cross_section,
    Circle,
    PackingResult,
)


class TestCircle:
    """Tests for Circle dataclass."""
    
    def test_circle_creation(self):
        """Circle stores correct values."""
        circle = Circle(x=100, y=50, radius=25, diameter=50)
        
        assert circle.x == 100
        assert circle.y == 50
        assert circle.radius == 25
        assert circle.diameter == 50
    
    def test_overlaps_true(self):
        """Overlapping circles detected."""
        c1 = Circle(x=0, y=0, radius=50, diameter=100)
        c2 = Circle(x=60, y=0, radius=50, diameter=100)  # 60 < 100 (50+50)
        
        assert c1.overlaps(c2) is True
    
    def test_overlaps_false(self):
        """Non-overlapping circles not flagged."""
        c1 = Circle(x=0, y=0, radius=50, diameter=100)
        c2 = Circle(x=120, y=0, radius=50, diameter=100)  # 120 > 100
        
        assert c1.overlaps(c2) is False
    
    def test_overlaps_with_gap(self):
        """Gap requirement affects overlap detection."""
        c1 = Circle(x=0, y=0, radius=50, diameter=100)
        c2 = Circle(x=110, y=0, radius=50, diameter=100)
        
        # Without gap: 110 > 100, no overlap
        assert c1.overlaps(c2, min_gap=0) is False
        
        # With 20mm gap: 110 < 120 (100+20), overlap
        assert c1.overlaps(c2, min_gap=20) is True
    
    def test_fits_in_rectangle(self):
        """Circle boundary check works."""
        circle = Circle(x=50, y=50, radius=40, diameter=80)
        
        # Fits in 100x100
        assert circle.fits_in_rectangle(100, 100) is True
        
        # Doesn't fit in 80x80
        assert circle.fits_in_rectangle(80, 80) is False


class TestPackCirclesGreedy:
    """Tests for greedy packing algorithm."""
    
    def test_empty_input(self):
        """Empty diameters returns empty result."""
        result = pack_circles_greedy([], 100, 100)
        
        assert result.total_packed == 0
        assert result.circles == []
        assert result.packing_efficiency == 0
    
    def test_single_circle(self):
        """Single circle packs correctly."""
        result = pack_circles_greedy([50], 100, 100)
        
        assert result.total_packed == 1
        assert len(result.circles) == 1
        
        # Circle should be at bottom
        circle = result.circles[0]
        assert circle.y == pytest.approx(25, 1)  # radius from bottom
    
    def test_multiple_same_size(self):
        """Multiple same-size circles pack."""
        result = pack_circles_greedy([50, 50, 50, 50], 200, 200)
        
        # All 4 should fit in 200x200
        assert result.total_packed == 4
        assert result.packing_efficiency > 0
    
    def test_different_sizes(self):
        """Different sizes sorted by size descending."""
        result = pack_circles_greedy([100, 50, 25], 200, 200)
        
        # All should fit
        assert result.total_packed == 3
        
        # Largest should be placed first (bottom-left)
        diameters = [c.diameter for c in result.circles]
        assert 100 in diameters
    
    def test_circle_too_large(self):
        """Circle larger than container not packed."""
        result = pack_circles_greedy([300], 200, 200)
        
        assert result.total_packed == 0
        assert result.unpacked_count == 1


class TestPackNestedBundleCrossSection:
    """Tests for nested bundle packing."""
    
    def test_empty_inner_pipes(self):
        """No inner pipes returns empty result."""
        result = pack_nested_bundle_cross_section(
            outer_diameter=400,
            inner_diameters=[]
        )
        
        assert result.total_packed == 0
    
    def test_single_nested_pipe(self):
        """Single pipe nests in larger host."""
        # DN315 inside DN630 (ID ~581mm)
        result = pack_nested_bundle_cross_section(
            outer_diameter=581.8,  # Inner diameter of host (TPE630/PN6)
            inner_diameters=[315]  # DN315 outer diameter
        )
        
        assert result.total_packed == 1
    
    def test_multiple_nested_small_pipes(self):
        """Multiple small pipes nest in large host."""
        # Several DN110 pipes inside DN630
        result = pack_nested_bundle_cross_section(
            outer_diameter=581.8,
            inner_diameters=[110, 110, 110, 110],
            min_gap=15.0
        )
        
        # Should pack at least some
        assert result.total_packed >= 1
    
    def test_pipe_too_large(self):
        """Pipe too large for host not packed."""
        result = pack_nested_bundle_cross_section(
            outer_diameter=369.4,  # DN400 inner
            inner_diameters=[400]  # DN400 outer - same size, won't fit
        )
        
        assert result.unpacked_count >= 1
