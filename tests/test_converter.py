"""
Basic unit tests for the floor plan converter.
"""

import unittest
import numpy as np
import cv2
import os
import tempfile

from floor_plan_converter.config import Config
from floor_plan_converter.preprocessor import preprocess_image, apply_gaussian_blur, enhance_contrast
from floor_plan_converter.line_detector import detect_walls, merge_lines, point_to_line_distance
from floor_plan_converter.geometry import straighten_angle, snap_to_grid, line_intersection
from floor_plan_converter.renderer import render_output


class TestConfig(unittest.TestCase):
    """Test configuration class."""
    
    def test_config_defaults(self):
        """Test that default configuration is created correctly."""
        config = Config()
        self.assertEqual(config.DEFAULT_WALL_THICKNESS, 6)
        self.assertEqual(config.DEFAULT_UNITS, 'metric')
        self.assertEqual(config.CANNY_THRESHOLD1, 50)
    
    def test_config_override(self):
        """Test that configuration can be overridden."""
        config = Config(default_wall_thickness=10)
        self.assertEqual(config.DEFAULT_WALL_THICKNESS, 10)


class TestPreprocessor(unittest.TestCase):
    """Test preprocessing functions."""
    
    def setUp(self):
        """Create test image."""
        self.test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        self.test_gray = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
    
    def test_preprocess_image(self):
        """Test image preprocessing."""
        result = preprocess_image(self.test_image)
        self.assertEqual(result.shape, (100, 100))
        self.assertEqual(result.dtype, np.uint8)
    
    def test_gaussian_blur(self):
        """Test Gaussian blur."""
        result = apply_gaussian_blur(self.test_gray)
        self.assertEqual(result.shape, self.test_gray.shape)
    
    def test_enhance_contrast(self):
        """Test contrast enhancement."""
        result = enhance_contrast(self.test_gray)
        self.assertEqual(result.shape, self.test_gray.shape)


class TestLineDetector(unittest.TestCase):
    """Test line detection functions."""
    
    def test_point_to_line_distance(self):
        """Test distance calculation from point to line."""
        # Horizontal line from (0,0) to (10,0)
        line = (0, 0, 10, 0)
        # Point above the line
        point = (5, 5)
        distance = point_to_line_distance(point, line)
        self.assertAlmostEqual(distance, 5.0, places=1)
    
    def test_merge_lines_empty(self):
        """Test merging with empty list."""
        config = Config()
        result = merge_lines([], config)
        self.assertEqual(result, [])


class TestGeometry(unittest.TestCase):
    """Test geometry functions."""
    
    def test_straighten_angle(self):
        """Test angle straightening."""
        # Test snapping to 0 degrees
        self.assertEqual(straighten_angle(3), 0)
        self.assertEqual(straighten_angle(-2), 0)
        
        # Test snapping to 90 degrees
        self.assertEqual(straighten_angle(88), 90)
        self.assertEqual(straighten_angle(92), 90)
        
        # Test no snapping
        self.assertEqual(straighten_angle(30, threshold=5), 30)
    
    def test_snap_to_grid(self):
        """Test grid snapping."""
        # Test snapping to 10-pixel grid
        x, y = snap_to_grid(23, 47, grid_size=10)
        self.assertEqual(x, 20)
        self.assertEqual(y, 50)
    
    def test_line_intersection(self):
        """Test line intersection calculation."""
        # Two intersecting lines
        line1 = (0, 0, 10, 10)  # Diagonal
        line2 = (0, 10, 10, 0)  # Other diagonal
        
        intersection = line_intersection(line1, line2)
        self.assertIsNotNone(intersection)
        # Should intersect at approximately (5, 5)
        self.assertAlmostEqual(intersection[0], 5, delta=1)
        self.assertAlmostEqual(intersection[1], 5, delta=1)
    
    def test_parallel_lines_no_intersection(self):
        """Test that parallel lines don't intersect."""
        line1 = (0, 0, 10, 0)  # Horizontal
        line2 = (0, 5, 10, 5)  # Parallel horizontal
        
        intersection = line_intersection(line1, line2)
        self.assertIsNone(intersection)


class TestRenderer(unittest.TestCase):
    """Test rendering functions."""
    
    def test_render_png_output(self):
        """Test PNG rendering."""
        # Create test data
        image_shape = (100, 100)
        lines = [
            ((10, 10, 90, 10), 0, 80),
            ((10, 10, 10, 90), 90, 80),
        ]
        
        # Use temporary file for cross-platform compatibility
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            # Render
            result = render_output(
                image_shape,
                lines,
                output_path=output_path,
                format='png'
            )
            
            # Check file was created
            self.assertTrue(os.path.exists(result))
            
            # Verify it's a valid image
            img = cv2.imread(result)
            self.assertIsNotNone(img)
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.remove(output_path)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_pipeline(self):
        """Test the complete processing pipeline."""
        # Create a simple test image with a rectangle
        img = np.ones((200, 200, 3), dtype=np.uint8) * 255
        cv2.rectangle(img, (50, 50), (150, 150), (0, 0, 0), 3)
        
        # Process
        config = Config()
        preprocessed = preprocess_image(img, config)
        lines = detect_walls(preprocessed, config)
        
        # Should detect some lines
        self.assertGreater(len(lines), 0)


if __name__ == '__main__':
    unittest.main()
