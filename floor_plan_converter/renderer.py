"""
Output rendering functions for generating CAD-style drawings.
"""

import cv2
import numpy as np
import svgwrite
from PIL import Image
import json
from .config import Config


def render_output(image_shape, lines, rooms=None, output_path='output.png', 
                  config=None, add_dimensions=False, format='png'):
    """
    Render the processed floor plan to output file.
    
    Args:
        image_shape: Original image shape (height, width)
        lines: List of detected and corrected lines
        rooms: Optional list of detected room contours
        output_path: Path to save output file
        config: Config instance
        add_dimensions: Whether to add dimension annotations
        format: Output format ('png' or 'svg')
        
    Returns:
        Path to the generated output file
    """
    if config is None:
        config = Config()
    
    if format.lower() == 'svg':
        return render_svg(image_shape, lines, rooms, output_path, config, add_dimensions)
    else:
        return render_png(image_shape, lines, rooms, output_path, config, add_dimensions)


def render_png(image_shape, lines, rooms, output_path, config, add_dimensions):
    """
    Render output as PNG image.
    
    Args:
        image_shape: Original image shape (height, width)
        lines: List of detected and corrected lines
        rooms: Optional list of detected room contours
        output_path: Path to save output file
        config: Config instance
        add_dimensions: Whether to add dimension annotations
        
    Returns:
        Path to the generated PNG file
    """
    height, width = image_shape[:2]
    
    # Create blank white canvas
    output = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw walls
    for (x1, y1, x2, y2), angle, length in lines:
        # Determine wall thickness based on angle (exterior vs interior)
        thickness = config.DEFAULT_WALL_THICKNESS
        
        cv2.line(output, (x1, y1), (x2, y2), config.LINE_COLOR, thickness)
    
    # Draw room labels if rooms are provided
    if rooms and len(rooms) > 0:
        for i, room in enumerate(rooms):
            # Calculate room center
            M = cv2.moments(room)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Add room label
                label = f"Room {i+1}"
                cv2.putText(output, label, (cx-30, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
    
    # Add dimensions if requested
    if add_dimensions and lines:
        add_dimension_annotations(output, lines, config)
    
    # Save output
    cv2.imwrite(output_path, output)
    
    return output_path


def render_svg(image_shape, lines, rooms, output_path, config, add_dimensions):
    """
    Render output as SVG file.
    
    Args:
        image_shape: Original image shape (height, width)
        lines: List of detected and corrected lines
        rooms: Optional list of detected room contours
        output_path: Path to save output file
        config: Config instance
        add_dimensions: Whether to add dimension annotations
        
    Returns:
        Path to the generated SVG file
    """
    height, width = image_shape[:2]
    
    # Create SVG drawing
    dwg = svgwrite.Drawing(output_path, size=(width, height))
    
    # Add white background
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill='white'))
    
    # Draw walls
    for (x1, y1, x2, y2), angle, length in lines:
        thickness = config.DEFAULT_WALL_THICKNESS
        dwg.add(dwg.line(
            start=(x1, y1),
            end=(x2, y2),
            stroke='black',
            stroke_width=thickness,
            stroke_linecap='round'
        ))
    
    # Draw room labels if rooms are provided
    if rooms and len(rooms) > 0:
        for i, room in enumerate(rooms):
            # Calculate room center
            M = cv2.moments(room)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Add room label
                label = f"Room {i+1}"
                dwg.add(dwg.text(
                    label,
                    insert=(cx, cy),
                    text_anchor='middle',
                    font_size='14px',
                    font_family='Arial',
                    fill='gray'
                ))
    
    # Add dimensions if requested
    if add_dimensions and lines:
        add_svg_dimensions(dwg, lines, config)
    
    # Save SVG
    dwg.save()
    
    return output_path


def add_dimension_annotations(image, lines, config):
    """
    Add dimension annotations to PNG output.
    
    Args:
        image: Output image (modified in place)
        lines: List of lines with dimensions
        config: Config instance
    """
    # Sample a few lines to add dimensions
    scale = config.PIXEL_TO_METER if config.DEFAULT_UNITS == 'metric' else config.PIXEL_TO_FEET
    unit = 'm' if config.DEFAULT_UNITS == 'metric' else 'ft'
    
    # Add dimensions to longest lines
    sorted_lines = sorted(lines, key=lambda x: x[2], reverse=True)
    
    for i, ((x1, y1, x2, y2), angle, length) in enumerate(sorted_lines[:5]):
        # Calculate real-world length
        real_length = length * scale
        
        # Calculate midpoint
        mx = (x1 + x2) // 2
        my = (y1 + y2) // 2
        
        # Add dimension text
        text = f"{real_length:.2f}{unit}"
        cv2.putText(image, text, (mx, my - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (50, 50, 200), 1)


def add_svg_dimensions(dwg, lines, config):
    """
    Add dimension annotations to SVG output.
    
    Args:
        dwg: SVG drawing object
        lines: List of lines with dimensions
        config: Config instance
    """
    scale = config.PIXEL_TO_METER if config.DEFAULT_UNITS == 'metric' else config.PIXEL_TO_FEET
    unit = 'm' if config.DEFAULT_UNITS == 'metric' else 'ft'
    
    # Add dimensions to longest lines
    sorted_lines = sorted(lines, key=lambda x: x[2], reverse=True)
    
    for i, ((x1, y1, x2, y2), angle, length) in enumerate(sorted_lines[:5]):
        # Calculate real-world length
        real_length = length * scale
        
        # Calculate midpoint
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        
        # Add dimension text
        text = f"{real_length:.2f}{unit}"
        dwg.add(dwg.text(
            text,
            insert=(mx, my - 5),
            font_size='12px',
            font_family='Arial',
            fill='blue'
        ))


def export_to_json(lines, rooms, output_path, config=None):
    """
    Export floor plan data to JSON format for CAD software import.
    
    Args:
        lines: List of detected lines
        rooms: List of detected room contours
        output_path: Path to save JSON file
        config: Config instance
        
    Returns:
        Path to the generated JSON file
    """
    if config is None:
        config = Config()
    
    data = {
        'version': '1.0',
        'units': config.DEFAULT_UNITS,
        'scale': config.PIXEL_TO_METER if config.DEFAULT_UNITS == 'metric' else config.PIXEL_TO_FEET,
        'walls': [],
        'rooms': []
    }
    
    # Add wall data
    for (x1, y1, x2, y2), angle, length in lines:
        data['walls'].append({
            'start': {'x': int(x1), 'y': int(y1)},
            'end': {'x': int(x2), 'y': int(y2)},
            'angle': float(angle),
            'length': float(length)
        })
    
    # Add room data
    if rooms:
        for i, room in enumerate(rooms):
            # Get bounding box
            x, y, w, h = cv2.boundingRect(room)
            area = cv2.contourArea(room)
            
            data['rooms'].append({
                'id': i + 1,
                'bounding_box': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                'area': float(area)
            })
    
    # Save JSON
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return output_path


def create_visualization(original_image, processed_image, lines, output_path):
    """
    Create a side-by-side visualization of original and processed images.
    
    Args:
        original_image: Original input image
        processed_image: Processed output image
        lines: List of detected lines
        output_path: Path to save visualization
        
    Returns:
        Path to the generated visualization
    """
    # Resize images if needed
    h1, w1 = original_image.shape[:2]
    h2, w2 = processed_image.shape[:2]
    
    max_height = max(h1, h2)
    
    # Create combined image
    combined = np.ones((max_height, w1 + w2 + 20, 3), dtype=np.uint8) * 255
    
    # Place original image
    if len(original_image.shape) == 2:
        original_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
    combined[:h1, :w1] = original_image
    
    # Place processed image
    combined[:h2, w1+20:w1+20+w2] = processed_image
    
    # Add labels
    cv2.putText(combined, "Original", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(combined, "Processed", (w1 + 30, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Save visualization
    cv2.imwrite(output_path, combined)
    
    return output_path
