"""
Circle Packing Algorithm

Simplified 2D circle packing in a rectangle for pipe cross-section visualization.
Full circle packing is NP-hard; this uses a greedy approach.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Circle:
    """A circle with position and radius."""
    x: float  # Center X
    y: float  # Center Y
    radius: float
    diameter: float
    pipe_code: Optional[str] = None
    
    def overlaps(self, other: "Circle", min_gap: float = 0) -> bool:
        """Check if this circle overlaps with another."""
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return distance < (self.radius + other.radius + min_gap)
    
    def fits_in_rectangle(
        self, width: float, height: float, min_margin: float = 0
    ) -> bool:
        """Check if circle fits within rectangle bounds."""
        return (
            self.x - self.radius >= min_margin and
            self.x + self.radius <= width - min_margin and
            self.y - self.radius >= min_margin and
            self.y + self.radius <= height - min_margin
        )


@dataclass
class PackingResult:
    """Result of circle packing."""
    circles: List[Circle]
    total_packed: int
    container_width: float
    container_height: float
    packing_efficiency: float  # Ratio of circle area to container area
    unpacked_count: int


def pack_circles_greedy(
    diameters: List[float],
    container_width: float,
    container_height: float,
    pipe_codes: Optional[List[str]] = None,
    min_gap: float = 0
) -> PackingResult:
    """
    Pack circles into rectangle using greedy bottom-left algorithm.
    
    Strategy:
    1. Sort circles by diameter descending
    2. For each circle, find lowest available position
    3. Place circle at bottom-left most valid position
    
    Args:
        diameters: List of circle diameters to pack
        container_width: Container width
        container_height: Container height
        pipe_codes: Optional pipe codes for labeling
        min_gap: Minimum gap between circles
        
    Returns:
        PackingResult with placed circles
    """
    if not diameters:
        return PackingResult(
            circles=[], total_packed=0,
            container_width=container_width,
            container_height=container_height,
            packing_efficiency=0, unpacked_count=0
        )
    
    # Create indexed list for sorting while preserving codes
    indexed_diameters = list(enumerate(diameters))
    indexed_diameters.sort(key=lambda x: x[1], reverse=True)
    
    placed_circles: List[Circle] = []
    unpacked = 0
    
    for idx, diameter in indexed_diameters:
        radius = diameter / 2
        code = pipe_codes[idx] if pipe_codes and idx < len(pipe_codes) else None
        
        # Try to find valid position
        best_pos = find_lowest_position(
            radius, container_width, container_height,
            placed_circles, min_gap
        )
        
        if best_pos:
            x, y = best_pos
            circle = Circle(
                x=x, y=y, radius=radius, 
                diameter=diameter, pipe_code=code
            )
            placed_circles.append(circle)
        else:
            unpacked += 1
    
    # Calculate efficiency
    total_circle_area = sum(math.pi * c.radius**2 for c in placed_circles)
    container_area = container_width * container_height
    efficiency = total_circle_area / container_area if container_area > 0 else 0
    
    return PackingResult(
        circles=placed_circles,
        total_packed=len(placed_circles),
        container_width=container_width,
        container_height=container_height,
        packing_efficiency=efficiency,
        unpacked_count=unpacked
    )


def find_lowest_position(
    radius: float,
    container_width: float,
    container_height: float,
    placed_circles: List[Circle],
    min_gap: float = 0
) -> Optional[Tuple[float, float]]:
    """
    Find the lowest valid position for a circle.
    
    Scans potential positions and returns bottom-left most valid one.
    """
    diameter = radius * 2
    
    # Generate candidate positions
    candidates = []
    
    # Try floor positions (bottom of container)
    for x in range_float(radius, container_width - radius, diameter / 4):
        y = radius
        if is_valid_position(x, y, radius, container_width, container_height,
                            placed_circles, min_gap):
            candidates.append((x, y))
    
    # Try positions on top of existing circles
    for existing in placed_circles:
        # Directly on top
        x = existing.x
        y = existing.y + existing.radius + radius + min_gap
        if is_valid_position(x, y, radius, container_width, container_height,
                            placed_circles, min_gap):
            candidates.append((x, y))
        
        # To the left and right (touching)
        for dx in [-1, 1]:
            # Horizontal touch
            x = existing.x + dx * (existing.radius + radius + min_gap)
            y = existing.y
            if is_valid_position(x, y, radius, container_width, container_height,
                                placed_circles, min_gap):
                candidates.append((x, y))
            
            # Diagonal (hexagonal stacking position)
            x = existing.x + dx * (existing.radius + radius) * 0.5
            dy = math.sqrt((existing.radius + radius)**2 - 
                          ((existing.radius + radius) * 0.5)**2)
            y = existing.y + dy + min_gap/2
            if is_valid_position(x, y, radius, container_width, container_height,
                                placed_circles, min_gap):
                candidates.append((x, y))
    
    if not candidates:
        return None
    
    # Return lowest (then leftmost) position
    candidates.sort(key=lambda p: (p[1], p[0]))
    return candidates[0]


def is_valid_position(
    x: float, y: float, radius: float,
    container_width: float, container_height: float,
    placed_circles: List[Circle], min_gap: float
) -> bool:
    """Check if position is valid (within bounds and no overlaps)."""
    # Check bounds
    if x - radius < 0 or x + radius > container_width:
        return False
    if y - radius < 0 or y + radius > container_height:
        return False
    
    # Check overlaps
    for existing in placed_circles:
        distance = math.sqrt((x - existing.x)**2 + (y - existing.y)**2)
        if distance < radius + existing.radius + min_gap:
            return False
    
    return True


def range_float(start: float, end: float, step: float):
    """Generate float range."""
    current = start
    while current <= end:
        yield current
        current += step


def pack_nested_bundle_cross_section(
    outer_diameter: float,
    inner_diameters: List[float],
    min_gap: float = 15.0
) -> PackingResult:
    """
    Pack smaller circles inside a larger circle (nested pipe bundle).
    
    Args:
        outer_diameter: Outer (host) pipe inner diameter
        inner_diameters: List of inner pipe outer diameters
        min_gap: Minimum gap between pipes
        
    Returns:
        PackingResult with positions of inner pipes
    """
    outer_radius = outer_diameter / 2
    
    # Sort by size descending
    sorted_diameters = sorted(inner_diameters, reverse=True)
    
    placed: List[Circle] = []
    unpacked = 0
    
    for diameter in sorted_diameters:
        radius = diameter / 2
        
        # Find valid position inside outer circle
        best_pos = find_position_in_circle(
            radius, outer_radius, placed, min_gap
        )
        
        if best_pos:
            x, y = best_pos
            placed.append(Circle(x=x, y=y, radius=radius, diameter=diameter))
        else:
            unpacked += 1
    
    # Calculate efficiency (area ratio)
    inner_area = sum(math.pi * c.radius**2 for c in placed)
    outer_area = math.pi * outer_radius**2
    efficiency = inner_area / outer_area if outer_area > 0 else 0
    
    return PackingResult(
        circles=placed,
        total_packed=len(placed),
        container_width=outer_diameter,
        container_height=outer_diameter,
        packing_efficiency=efficiency,
        unpacked_count=unpacked
    )


def find_position_in_circle(
    radius: float,
    container_radius: float,
    placed_circles: List[Circle],
    min_gap: float
) -> Optional[Tuple[float, float]]:
    """Find valid position for circle inside circular container."""
    # Center of container is at (0, 0) for simplicity
    
    # Try center first
    if is_valid_in_circle(0, 0, radius, container_radius, placed_circles, min_gap):
        return (0, 0)
    
    # Try positions around existing circles
    for existing in placed_circles:
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            distance = existing.radius + radius + min_gap
            x = existing.x + distance * math.cos(rad)
            y = existing.y + distance * math.sin(rad)
            
            if is_valid_in_circle(x, y, radius, container_radius, 
                                  placed_circles, min_gap):
                return (x, y)
    
    # Try ring positions near container edge
    for ring_radius in [container_radius * 0.3, container_radius * 0.5, 
                        container_radius * 0.7]:
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            x = ring_radius * math.cos(rad)
            y = ring_radius * math.sin(rad)
            
            if is_valid_in_circle(x, y, radius, container_radius,
                                  placed_circles, min_gap):
                return (x, y)
    
    return None


def is_valid_in_circle(
    x: float, y: float, radius: float,
    container_radius: float,
    placed_circles: List[Circle],
    min_gap: float
) -> bool:
    """Check if position is valid inside circular container."""
    # Check if within container
    distance_from_center = math.sqrt(x**2 + y**2)
    if distance_from_center + radius + min_gap/2 > container_radius:
        return False
    
    # Check overlaps with placed circles
    for existing in placed_circles:
        distance = math.sqrt((x - existing.x)**2 + (y - existing.y)**2)
        if distance < radius + existing.radius + min_gap:
            return False
    
    return True


def visualize_packing_ascii(result: PackingResult, width: int = 60) -> str:
    """
    Generate ASCII visualization of packing result.
    
    For debugging and simple visualization.
    """
    if not result.circles:
        return "Empty packing"
    
    scale = width / result.container_width
    height = int(result.container_height * scale)
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Draw circles as characters
    for i, circle in enumerate(result.circles):
        cx = int(circle.x * scale)
        cy = int(circle.y * scale)
        r = max(1, int(circle.radius * scale))
        char = chr(ord('A') + i % 26)
        
        # Simple circle drawing
        for dy in range(-r, r+1):
            for dx in range(-r, r+1):
                if dx*dx + dy*dy <= r*r:
                    py = cy + dy
                    px = cx + dx
                    if 0 <= py < height and 0 <= px < width:
                        grid[py][px] = char
    
    # Convert to string
    lines = [''.join(row) for row in reversed(grid)]
    return '\n'.join(lines)
