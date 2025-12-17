"""
Geometry correction and manipulation utilities.
"""

import numpy as np
from .config import Config


def correct_geometry(lines, config=None):
    """
    Correct line geometry by straightening angles and ensuring proper proportions.
    
    Args:
        lines: List of lines as ((x1, y1, x2, y2), angle, length) tuples
        config: Config instance
        
    Returns:
        List of corrected lines
    """
    if config is None:
        config = Config()
    
    corrected_lines = []
    
    for coords, angle, length in lines:
        # Straighten angle to nearest 0°, 45°, or 90°
        corrected_angle = straighten_angle(angle, config.ANGLE_THRESHOLD)
        
        # Recalculate line endpoints based on corrected angle
        x1, y1, x2, y2 = coords
        corrected_coords = recalculate_line(x1, y1, x2, y2, corrected_angle)
        
        corrected_lines.append((corrected_coords, corrected_angle, length))
    
    return corrected_lines


def straighten_angle(angle, threshold=5):
    """
    Straighten angle to nearest cardinal direction (0°, 45°, 90°, etc.).
    
    Args:
        angle: Input angle in degrees
        threshold: Threshold for snapping to cardinal angles
        
    Returns:
        Corrected angle
    """
    # Normalize angle to [-180, 180]
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    
    # Define cardinal angles
    cardinal_angles = [0, 45, 90, 135, -180, -135, -90, -45]
    
    # Find nearest cardinal angle
    for cardinal in cardinal_angles:
        if abs(angle - cardinal) < threshold:
            return cardinal
    
    return angle


def recalculate_line(x1, y1, x2, y2, angle):
    """
    Recalculate line endpoints based on a new angle.
    
    Args:
        x1, y1: Start point
        x2, y2: End point
        angle: New angle in degrees
        
    Returns:
        New line coordinates (x1, y1, x2, y2)
    """
    # Calculate center point
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    
    # Calculate length
    length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Calculate new endpoints
    angle_rad = np.radians(angle)
    dx = length / 2 * np.cos(angle_rad)
    dy = length / 2 * np.sin(angle_rad)
    
    x1_new = int(cx - dx)
    y1_new = int(cy - dy)
    x2_new = int(cx + dx)
    y2_new = int(cy + dy)
    
    return (x1_new, y1_new, x2_new, y2_new)


def extend_line(x1, y1, x2, y2, extension=10):
    """
    Extend a line by a specified amount at both ends.
    
    Args:
        x1, y1: Start point
        x2, y2: End point
        extension: Number of pixels to extend
        
    Returns:
        Extended line coordinates (x1, y1, x2, y2)
    """
    # Calculate direction vector
    dx = x2 - x1
    dy = y2 - y1
    length = np.sqrt(dx**2 + dy**2)
    
    if length == 0:
        return (x1, y1, x2, y2)
    
    # Normalize direction vector
    dx /= length
    dy /= length
    
    # Extend endpoints
    x1_new = int(x1 - extension * dx)
    y1_new = int(y1 - extension * dy)
    x2_new = int(x2 + extension * dx)
    y2_new = int(y2 + extension * dy)
    
    return (x1_new, y1_new, x2_new, y2_new)


def snap_to_grid(x, y, grid_size=10):
    """
    Snap a point to the nearest grid intersection.
    
    Args:
        x, y: Point coordinates
        grid_size: Grid spacing in pixels
        
    Returns:
        Snapped coordinates (x, y)
    """
    x_snapped = round(x / grid_size) * grid_size
    y_snapped = round(y / grid_size) * grid_size
    
    return (int(x_snapped), int(y_snapped))


def find_line_intersections(lines):
    """
    Find intersection points between lines.
    
    Args:
        lines: List of lines as ((x1, y1, x2, y2), angle, length) tuples
        
    Returns:
        List of intersection points
    """
    intersections = []
    
    for i, (coords1, _, _) in enumerate(lines):
        for j, (coords2, _, _) in enumerate(lines):
            if i >= j:
                continue
            
            intersection = line_intersection(coords1, coords2)
            if intersection is not None:
                intersections.append(intersection)
    
    return intersections


def line_intersection(line1, line2):
    """
    Calculate intersection point between two lines.
    
    Args:
        line1: (x1, y1, x2, y2) coordinates
        line2: (x3, y3, x4, y4) coordinates
        
    Returns:
        Intersection point (x, y) or None if lines don't intersect
    """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    
    # Calculate denominators
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if abs(denom) < 1e-10:
        return None  # Lines are parallel
    
    # Calculate intersection point
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    # Check if intersection is within line segments
    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (int(x), int(y))
    
    return None


def calculate_scale(image_shape, reference_length_pixels, reference_length_real, units='metric'):
    """
    Calculate pixel-to-real-world scale factor.
    
    Args:
        image_shape: Shape of the image (height, width)
        reference_length_pixels: Known length in pixels
        reference_length_real: Corresponding real-world length
        units: 'metric' (meters) or 'imperial' (feet)
        
    Returns:
        Scale factor (real units per pixel)
    """
    if reference_length_pixels <= 0:
        return Config.PIXEL_TO_METER if units == 'metric' else Config.PIXEL_TO_FEET
    
    scale = reference_length_real / reference_length_pixels
    return scale
