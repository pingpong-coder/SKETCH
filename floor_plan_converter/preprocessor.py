"""
Image preprocessing functions for floor plan conversion.
"""

import cv2
import numpy as np
from .config import Config


def preprocess_image(image, config=None):
    """
    Preprocess the input floor plan image.
    
    This function performs grayscale conversion, noise reduction,
    and contrast enhancement to prepare the image for line detection.
    
    Args:
        image: Input image (BGR format from cv2.imread)
        config: Config instance with preprocessing parameters
        
    Returns:
        Preprocessed grayscale image
    """
    if config is None:
        config = Config()
    
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply bilateral filter for noise reduction while preserving edges
    filtered = cv2.bilateralFilter(
        gray,
        config.BILATERAL_FILTER_D,
        config.BILATERAL_FILTER_SIGMA_COLOR,
        config.BILATERAL_FILTER_SIGMA_SPACE
    )
    
    # Enhance contrast using adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(filtered)
    
    return enhanced


def apply_gaussian_blur(image, kernel_size=(5, 5)):
    """
    Apply Gaussian blur to reduce noise.
    
    Args:
        image: Input grayscale image
        kernel_size: Size of the Gaussian kernel
        
    Returns:
        Blurred image
    """
    return cv2.GaussianBlur(image, kernel_size, 0)


def enhance_contrast(image, clip_limit=2.0, tile_size=(8, 8)):
    """
    Enhance image contrast using CLAHE.
    
    Args:
        image: Input grayscale image
        clip_limit: Threshold for contrast limiting
        tile_size: Size of grid for histogram equalization
        
    Returns:
        Contrast-enhanced image
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    return clahe.apply(image)


def apply_morphology(image, operation='close', kernel_size=(3, 3)):
    """
    Apply morphological operations to clean up the image.
    
    Args:
        image: Input binary image
        operation: Morphological operation ('open', 'close', 'dilate', 'erode')
        kernel_size: Size of the structuring element
        
    Returns:
        Processed image
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    
    if operation == 'open':
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    elif operation == 'close':
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    elif operation == 'dilate':
        return cv2.dilate(image, kernel, iterations=1)
    elif operation == 'erode':
        return cv2.erode(image, kernel, iterations=1)
    else:
        return image


def correct_perspective(image, corners=None):
    """
    Correct perspective distortion in the image.
    
    Args:
        image: Input image
        corners: Optional list of 4 corner points [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
                 If None, attempts automatic detection
        
    Returns:
        Perspective-corrected image
    """
    if corners is None:
        # Automatic corner detection (simplified)
        # For a more robust implementation, you'd want to detect the floor plan boundary
        return image
    
    # Convert corners to numpy array
    src_points = np.array(corners, dtype=np.float32)
    
    # Calculate output size
    width = max(
        np.linalg.norm(src_points[0] - src_points[1]),
        np.linalg.norm(src_points[2] - src_points[3])
    )
    height = max(
        np.linalg.norm(src_points[0] - src_points[3]),
        np.linalg.norm(src_points[1] - src_points[2])
    )
    
    # Define destination points
    dst_points = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype=np.float32)
    
    # Calculate perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    
    # Apply perspective transform
    corrected = cv2.warpPerspective(image, matrix, (int(width), int(height)))
    
    return corrected
