"""
Configuration settings for the floor plan converter.
"""


class Config:
    """Configuration class for floor plan conversion parameters."""
    
    # Image preprocessing
    GAUSSIAN_BLUR_KERNEL = (5, 5)
    BILATERAL_FILTER_D = 9
    BILATERAL_FILTER_SIGMA_COLOR = 75
    BILATERAL_FILTER_SIGMA_SPACE = 75
    
    # Edge detection
    CANNY_THRESHOLD1 = 50
    CANNY_THRESHOLD2 = 150
    CANNY_APERTURE_SIZE = 3
    
    # Hough Line Transform
    HOUGH_RHO = 1
    HOUGH_THETA = 1  # degrees
    HOUGH_THRESHOLD = 100
    HOUGH_MIN_LINE_LENGTH = 50
    HOUGH_MAX_LINE_GAP = 10
    
    # Line processing
    ANGLE_THRESHOLD = 5  # degrees for line straightening
    LINE_MERGE_DISTANCE = 10  # pixels
    LINE_MERGE_ANGLE = 5  # degrees
    
    # Wall rendering
    DEFAULT_WALL_THICKNESS = 6  # pixels
    INTERIOR_WALL_THICKNESS = 6  # pixels
    EXTERIOR_WALL_THICKNESS = 10  # pixels
    
    # Output settings
    OUTPUT_DPI = 300
    OUTPUT_FORMAT = "png"  # png or svg
    BACKGROUND_COLOR = (255, 255, 255)  # white
    LINE_COLOR = (0, 0, 0)  # black
    
    # Dimensions
    DEFAULT_UNITS = "metric"  # metric or imperial
    PIXEL_TO_METER = 0.01  # default scale
    PIXEL_TO_FEET = 0.0328  # default scale
    
    # Room detection
    MIN_ROOM_AREA = 1000  # pixels squared
    MAX_ROOM_AREA = 1000000  # pixels squared
    
    def __init__(self, **kwargs):
        """
        Initialize configuration with optional overrides.
        
        Args:
            **kwargs: Configuration parameters to override defaults.
                     Parameter names should be in lowercase with underscores
                     (e.g., 'default_wall_thickness') and will be automatically
                     converted to uppercase class attributes.
        """
        for key, value in kwargs.items():
            if hasattr(self, key.upper()):
                setattr(self, key.upper(), value)
    
    @classmethod
    def from_dict(cls, config_dict):
        """
        Create Config instance from dictionary.
        
        Args:
            config_dict: Dictionary of configuration parameters
            
        Returns:
            Config instance
        """
        return cls(**config_dict)
