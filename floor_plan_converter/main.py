"""
Main CLI entry point for the floor plan converter.
"""

import argparse
import sys
import os
import cv2
from pathlib import Path

from .config import Config
from .preprocessor import preprocess_image
from .line_detector import detect_walls, detect_rooms
from .geometry import correct_geometry
from .renderer import render_output, export_to_json, create_visualization


def main():
    """Main entry point for the floor plan converter CLI."""
    parser = argparse.ArgumentParser(
        description='Convert hand-drawn floor plans to clean CAD-style drawings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s input.jpg -o output.png
  %(prog)s IMG-20230211-WA0005.jpg --output clean_floorplan.svg --format svg
  %(prog)s input.jpg --wall-thickness 8 --units metric --add-dimensions
  %(prog)s input.jpg --export-json data.json --add-rooms
        '''
    )
    
    # Required arguments
    parser.add_argument(
        'input',
        help='Input floor plan image file (JPG, PNG)'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        default='output.png',
        help='Output file path (default: output.png)'
    )
    
    parser.add_argument(
        '--format',
        choices=['png', 'svg'],
        default='png',
        help='Output format (default: png)'
    )
    
    # Processing options
    parser.add_argument(
        '--wall-thickness',
        type=int,
        default=6,
        help='Wall thickness in pixels (default: 6)'
    )
    
    parser.add_argument(
        '--units',
        choices=['metric', 'imperial'],
        default='metric',
        help='Measurement units (default: metric)'
    )
    
    parser.add_argument(
        '--add-dimensions',
        action='store_true',
        help='Add dimension annotations to output'
    )
    
    parser.add_argument(
        '--add-rooms',
        action='store_true',
        help='Detect and label rooms'
    )
    
    parser.add_argument(
        '--export-json',
        metavar='FILE',
        help='Export floor plan data to JSON file'
    )
    
    parser.add_argument(
        '--visualization',
        metavar='FILE',
        help='Create side-by-side visualization of original and processed images'
    )
    
    # Advanced options
    parser.add_argument(
        '--canny-threshold1',
        type=int,
        default=50,
        help='Canny edge detection lower threshold (default: 50)'
    )
    
    parser.add_argument(
        '--canny-threshold2',
        type=int,
        default=150,
        help='Canny edge detection upper threshold (default: 150)'
    )
    
    parser.add_argument(
        '--hough-threshold',
        type=int,
        default=100,
        help='Hough transform threshold (default: 100)'
    )
    
    parser.add_argument(
        '--min-line-length',
        type=int,
        default=50,
        help='Minimum line length in pixels (default: 50)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        return 1
    
    # Create config with custom parameters
    config_params = {
        'default_wall_thickness': args.wall_thickness,
        'default_units': args.units,
        'canny_threshold1': args.canny_threshold1,
        'canny_threshold2': args.canny_threshold2,
        'hough_threshold': args.hough_threshold,
        'hough_min_line_length': args.min_line_length,
    }
    config = Config(**config_params)
    
    try:
        if args.verbose:
            print(f"Loading image: {args.input}")
        
        # Load image
        image = cv2.imread(args.input)
        if image is None:
            print(f"Error: Failed to load image '{args.input}'", file=sys.stderr)
            return 1
        
        if args.verbose:
            print(f"Image shape: {image.shape}")
            print("Preprocessing image...")
        
        # Preprocess image
        preprocessed = preprocess_image(image, config)
        
        if args.verbose:
            print("Detecting walls...")
        
        # Detect walls
        lines = detect_walls(preprocessed, config)
        
        if args.verbose:
            print(f"Detected {len(lines)} lines")
            print("Correcting geometry...")
        
        # Correct geometry
        corrected_lines = correct_geometry(lines, config)
        
        # Detect rooms if requested
        rooms = None
        if args.add_rooms:
            if args.verbose:
                print("Detecting rooms...")
            rooms = detect_rooms(preprocessed, corrected_lines)
            if args.verbose:
                print(f"Detected {len(rooms) if rooms else 0} rooms")
        
        if args.verbose:
            print(f"Rendering output to {args.output}...")
        
        # Set output format from extension if not explicitly specified
        output_format = args.format
        if args.output.endswith('.svg'):
            output_format = 'svg'
        elif args.output.endswith('.png'):
            output_format = 'png'
        
        # Render output
        output_path = render_output(
            image.shape,
            corrected_lines,
            rooms=rooms,
            output_path=args.output,
            config=config,
            add_dimensions=args.add_dimensions,
            format=output_format
        )
        
        print(f"✓ Output saved to: {output_path}")
        
        # Export to JSON if requested
        if args.export_json:
            if args.verbose:
                print(f"Exporting data to {args.export_json}...")
            json_path = export_to_json(corrected_lines, rooms, args.export_json, config)
            print(f"✓ JSON data saved to: {json_path}")
        
        # Create visualization if requested
        if args.visualization:
            if args.verbose:
                print(f"Creating visualization at {args.visualization}...")
            
            # Render output for visualization
            output_image = cv2.imread(output_path)
            if output_format == 'svg':
                # For SVG, we need to render a PNG version for visualization
                temp_output = 'temp_output.png'
                render_output(
                    image.shape,
                    corrected_lines,
                    rooms=rooms,
                    output_path=temp_output,
                    config=config,
                    add_dimensions=args.add_dimensions,
                    format='png'
                )
                output_image = cv2.imread(temp_output)
                os.remove(temp_output)
            
            vis_path = create_visualization(image, output_image, corrected_lines, args.visualization)
            print(f"✓ Visualization saved to: {vis_path}")
        
        if args.verbose:
            print("Done!")
        
        return 0
        
    except Exception as e:
        print(f"Error processing floor plan: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
