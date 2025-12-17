# Floor Plan Converter

A Python-based tool that converts hand-drawn floor plan images into clean, CAD-style 2D architectural drawings.

## Features

- **Image Processing Pipeline**
  - Grayscale conversion and noise reduction
  - Contrast enhancement for better line detection
  - Canny edge detection for edge identification
  - Hough Line Transform for wall detection

- **Geometry Correction**
  - Automatic line straightening to 0°, 90°, or 45° angles
  - Line merging to remove duplicates
  - Perspective correction support

- **Professional Output**
  - Clean black-and-white CAD-style drawings
  - Standardized wall thickness
  - Room detection and labeling
  - Dimension annotations
  - Multiple output formats (PNG, SVG)
  - JSON export for CAD software

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pingpong-coder/SKETCH.git
   cd SKETCH
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip install opencv-python numpy matplotlib svgwrite pillow
   ```

## Requirements

- Python 3.8 or higher
- OpenCV (cv2)
- NumPy
- Matplotlib
- svgwrite
- Pillow

## Usage

### Basic Usage

Convert a hand-drawn floor plan to a clean PNG image:

```bash
python -m floor_plan_converter input_image.jpg -o output_drawing.png
```

### Process the Example Image

```bash
python -m floor_plan_converter IMG-20230211-WA0005.jpg -o clean_floorplan.png
```

### Advanced Options

**Generate SVG output:**
```bash
python -m floor_plan_converter IMG-20230211-WA0005.jpg \
  --output clean_floorplan.svg \
  --format svg
```

**Add dimensions and room labels:**
```bash
python -m floor_plan_converter IMG-20230211-WA0005.jpg \
  --output output.png \
  --add-dimensions \
  --add-rooms
```

**Custom wall thickness and units:**
```bash
python -m floor_plan_converter input.jpg \
  --output output.png \
  --wall-thickness 8 \
  --units imperial \
  --add-dimensions
```

**Export to JSON for CAD software:**
```bash
python -m floor_plan_converter input.jpg \
  --output output.png \
  --export-json floorplan_data.json
```

**Create side-by-side visualization:**
```bash
python -m floor_plan_converter input.jpg \
  --output output.png \
  --visualization comparison.png
```

**Fine-tune detection parameters:**
```bash
python -m floor_plan_converter input.jpg \
  --output output.png \
  --canny-threshold1 50 \
  --canny-threshold2 150 \
  --hough-threshold 100 \
  --min-line-length 50 \
  --verbose
```

### Command-Line Options

```
positional arguments:
  input                 Input floor plan image file (JPG, PNG)

optional arguments:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (default: output.png)
  --format {png,svg}    Output format (default: png)
  --wall-thickness N    Wall thickness in pixels (default: 6)
  --units {metric,imperial}
                        Measurement units (default: metric)
  --add-dimensions      Add dimension annotations to output
  --add-rooms           Detect and label rooms
  --export-json FILE    Export floor plan data to JSON file
  --visualization FILE  Create side-by-side visualization
  --canny-threshold1 N  Canny edge detection lower threshold (default: 50)
  --canny-threshold2 N  Canny edge detection upper threshold (default: 150)
  --hough-threshold N   Hough transform threshold (default: 100)
  --min-line-length N   Minimum line length in pixels (default: 50)
  --verbose             Print verbose output
```

## Project Structure

```
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── IMG-20230211-WA0005.jpg     # Example input image
├── floor_plan_converter/
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # Module entry point
│   ├── main.py                 # CLI entry point
│   ├── config.py               # Configuration settings
│   ├── preprocessor.py         # Image preprocessing functions
│   ├── line_detector.py        # Wall/line detection logic
│   ├── geometry.py             # Geometry correction utilities
│   └── renderer.py             # Output generation (PNG, SVG)
├── examples/
│   └── output/                 # Sample output directory
└── tests/
    └── test_converter.py       # Basic unit tests
```

## How It Works

1. **Preprocessing**: The input image is converted to grayscale, noise is reduced using bilateral filtering, and contrast is enhanced using CLAHE (Contrast Limited Adaptive Histogram Equalization).

2. **Edge Detection**: Canny edge detection identifies edges in the preprocessed image.

3. **Line Detection**: The Hough Line Transform detects straight lines (walls) from the edges.

4. **Line Processing**: Similar and overlapping lines are merged, and angles are straightened to cardinal directions (0°, 90°, 45°).

5. **Room Detection** (optional): Enclosed spaces are identified as rooms using contour detection.

6. **Rendering**: The processed data is rendered to a clean output format with standardized wall thickness and optional annotations.

## Output Formats

### PNG
High-resolution raster image suitable for printing and presentations.

### SVG
Scalable vector graphics format that can be edited in CAD software or vector graphics editors.

### JSON
Structured data format containing:
- Wall coordinates and properties
- Room information
- Scale and unit information

Example JSON structure:
```json
{
  "version": "1.0",
  "units": "metric",
  "scale": 0.01,
  "walls": [
    {
      "start": {"x": 100, "y": 200},
      "end": {"x": 500, "y": 200},
      "angle": 0.0,
      "length": 400.0
    }
  ],
  "rooms": [
    {
      "id": 1,
      "bounding_box": {"x": 100, "y": 100, "width": 300, "height": 200},
      "area": 60000.0
    }
  ]
}
```

## Configuration

The tool can be configured by modifying parameters in `floor_plan_converter/config.py` or by passing command-line arguments. Key parameters include:

- **Edge Detection**: Canny thresholds for sensitivity
- **Line Detection**: Hough transform parameters
- **Wall Thickness**: Standardized thickness for rendering
- **Angle Threshold**: Tolerance for line straightening
- **Scale**: Pixel-to-real-world conversion factors

## Examples

The `examples/output/` directory can contain sample outputs generated from the provided test image.

To generate examples:
```bash
# Basic conversion
python -m floor_plan_converter IMG-20230211-WA0005.jpg -o examples/output/basic.png

# With all features
python -m floor_plan_converter IMG-20230211-WA0005.jpg \
  -o examples/output/full_features.png \
  --add-dimensions \
  --add-rooms \
  --verbose

# SVG output
python -m floor_plan_converter IMG-20230211-WA0005.jpg \
  -o examples/output/vector.svg \
  --format svg
```

## Troubleshooting

### No lines detected
- Try adjusting Canny thresholds: `--canny-threshold1` and `--canny-threshold2`
- Lower the Hough threshold: `--hough-threshold 50`
- Reduce minimum line length: `--min-line-length 30`

### Too many lines detected
- Increase Canny thresholds for less sensitivity
- Increase Hough threshold: `--hough-threshold 150`
- Increase minimum line length: `--min-line-length 100`

### Poor image quality
- Ensure good lighting in the original photo
- Try preprocessing the image externally before conversion
- Adjust bilateral filter parameters in `config.py`

## Limitations

- Works best with clear, well-lit photos of floor plans
- May struggle with heavily shaded or low-contrast images
- Curved walls are approximated with straight lines
- Automatic room detection requires fully enclosed spaces

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.

## Acknowledgments

Built with:
- OpenCV for image processing
- NumPy for numerical computations
- Matplotlib for visualization
- svgwrite for SVG generation

## Contact

For questions or support, please open an issue on GitHub.
