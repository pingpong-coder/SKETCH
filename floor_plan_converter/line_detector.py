"""
Line and wall detection functions for floor plan conversion.
"""

import cv2
import numpy as np
from .config import Config


def detect_walls(preprocessed_image, config=None):
    """
    Detect walls and lines in the preprocessed floor plan image.
    
    Args:
        preprocessed_image: Preprocessed grayscale image
        config: Config instance with detection parameters
        
    Returns:
        List of detected lines as ((x1, y1, x2, y2), angle, length) tuples
    """
    if config is None:
        config = Config()
    
    # Apply Canny edge detection
    edges = cv2.Canny(
        preprocessed_image,
        config.CANNY_THRESHOLD1,
        config.CANNY_THRESHOLD2,
        apertureSize=config.CANNY_APERTURE_SIZE
    )
    
    # Apply Hough Line Transform
    lines = cv2.HoughLinesP(
        edges,
        config.HOUGH_RHO,
        np.pi / 180 * config.HOUGH_THETA,
        config.HOUGH_THRESHOLD,
        minLineLength=config.HOUGH_MIN_LINE_LENGTH,
        maxLineGap=config.HOUGH_MAX_LINE_GAP
    )
    
    if lines is None:
        return []
    
    # Process and filter lines
    processed_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        
        # Calculate angle and length
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        processed_lines.append(((x1, y1, x2, y2), angle, length))
    
    # Merge similar lines
    merged_lines = merge_lines(processed_lines, config)
    
    return merged_lines


def merge_lines(lines, config):
    """
    Merge similar and overlapping lines.
    
    Args:
        lines: List of lines as ((x1, y1, x2, y2), angle, length) tuples
        config: Config instance
        
    Returns:
        List of merged lines
    """
    if not lines:
        return []
    
    merged = []
    used = set()
    
    for i, (coords1, angle1, length1) in enumerate(lines):
        if i in used:
            continue
        
        x1, y1, x2, y2 = coords1
        similar_lines = [coords1]
        
        for j, (coords2, angle2, length2) in enumerate(lines):
            if i == j or j in used:
                continue
            
            # Check if lines are similar (close angle and position)
            angle_diff = abs(angle1 - angle2)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            if angle_diff < config.LINE_MERGE_ANGLE:
                # Check distance between lines
                x3, y3, x4, y4 = coords2
                dist = point_to_line_distance((x3, y3), (x1, y1, x2, y2))
                
                if dist < config.LINE_MERGE_DISTANCE:
                    similar_lines.append(coords2)
                    used.add(j)
        
        # Merge similar lines by averaging
        if len(similar_lines) > 1:
            all_points = []
            for coords in similar_lines:
                all_points.extend([(coords[0], coords[1]), (coords[2], coords[3])])
            
            # Fit a line through all points
            if len(all_points) >= 2:
                points = np.array(all_points)
                [vx, vy, x, y] = cv2.fitLine(points, cv2.DIST_L2, 0, 0.01, 0.01)
                
                # Find extents of the merged line
                t_min = float('inf')
                t_max = float('-inf')
                for px, py in all_points:
                    t = ((px - x) * vx + (py - y) * vy) / (vx**2 + vy**2)
                    t_min = min(t_min, t)
                    t_max = max(t_max, t)
                
                # Calculate endpoints
                x1_new = int(x + t_min * vx)
                y1_new = int(y + t_min * vy)
                x2_new = int(x + t_max * vx)
                y2_new = int(y + t_max * vy)
                
                coords = (x1_new, y1_new, x2_new, y2_new)
                angle = np.arctan2(y2_new - y1_new, x2_new - x1_new) * 180 / np.pi
                length = np.sqrt((x2_new - x1_new)**2 + (y2_new - y1_new)**2)
                
                merged.append((coords, angle, length))
        else:
            merged.append((coords1, angle1, length1))
    
    return merged


def point_to_line_distance(point, line):
    """
    Calculate perpendicular distance from a point to a line.
    
    Args:
        point: (x, y) coordinates
        line: (x1, y1, x2, y2) line coordinates
        
    Returns:
        Distance in pixels
    """
    x0, y0 = point
    x1, y1, x2, y2 = line
    
    # Handle vertical/horizontal lines
    dx = x2 - x1
    dy = y2 - y1
    
    if dx == 0 and dy == 0:
        return np.sqrt((x0 - x1)**2 + (y0 - y1)**2)
    
    # Calculate distance using cross product
    distance = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    distance /= np.sqrt(dx**2 + dy**2)
    
    return distance


def detect_rooms(image, lines):
    """
    Detect enclosed spaces (rooms) in the floor plan.
    
    Args:
        image: Preprocessed image
        lines: List of detected wall lines
        
    Returns:
        List of room contours
    """
    # Create a blank image
    h, w = image.shape[:2]
    room_mask = np.zeros((h, w), dtype=np.uint8)
    
    # Draw all detected walls
    for (x1, y1, x2, y2), _, _ in lines:
        cv2.line(room_mask, (x1, y1), (x2, y2), 255, 2)
    
    # Close gaps
    kernel = np.ones((5, 5), np.uint8)
    room_mask = cv2.morphologyEx(room_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(room_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by area
    config = Config()
    valid_rooms = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if config.MIN_ROOM_AREA < area < config.MAX_ROOM_AREA:
            valid_rooms.append(contour)
    
    return valid_rooms


def calculate_room_dimensions(contour, pixel_scale=0.01):
    """
    Calculate dimensions of a room from its contour.
    
    Args:
        contour: Room contour
        pixel_scale: Scale factor (meters or feet per pixel)
        
    Returns:
        Tuple of (width, height) in the specified units
    """
    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(contour)
    
    # Convert to real-world units
    width = w * pixel_scale
    height = h * pixel_scale
    
    return (width, height)
