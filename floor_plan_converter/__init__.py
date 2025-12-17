"""
Floor Plan Converter Package

A Python tool that converts hand-drawn floor plan images into clean,
CAD-style 2D architectural drawings.
"""

__version__ = "1.0.0"
__author__ = "SKETCH Project"

from .config import Config
from .preprocessor import preprocess_image
from .line_detector import detect_walls
from .geometry import correct_geometry
from .renderer import render_output

__all__ = [
    "Config",
    "preprocess_image",
    "detect_walls",
    "correct_geometry",
    "render_output",
]
