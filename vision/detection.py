import cv2
import glob
import numpy as np
from typing import List, Optional, Tuple, Dict
from settings.settings_manager import SettingsManager
from utils.logger import logger


settings_manager = SettingsManager()
settings = settings_manager.settings.get('settings', {})
DEFAULT_SCALES = settings.get('scales', [1.0])
DEFAULT_ROTATIONS = settings.get('rotations', [0])
REFS_FOLDER_PATH = settings.get('refs_folder', '')

# Find maps in the screenshot.
def find_maps(screenshot: np.ndarray, threshold: float = 0.6) -> List:
    all_matches = []    

    template_files = glob.glob(REFS_FOLDER_PATH)
    if not template_files:        
        logger.warning(f"Warning: No template files found!")
        return all_matches

    for template_file in template_files:
        for scale in DEFAULT_SCALES:
            for angle in DEFAULT_ROTATIONS:
                template, size = load_and_preprocess_template(template_file, scale, angle)
                if template is None:
                    continue
                
                # Template Matching
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                maps = np.where(result >= threshold)

                for y,x in zip(*maps):
                    confidence = result[y,x]                    
                    if confidence >= 0.70:
                        center_x = x + size[0] // 2
                        center_y = y + size[1] // 2                        
                        
                        # Verify the match point has map-like characteristics
                        if is_valid_map_region(screenshot, (center_x, center_y)):
                            match_info = {
                                'position': (x, y),
                                'size': size,
                                'confidence': float(confidence),
                                'template': template_file
                            }
                            all_matches.append(match_info)

    # Sort by Confidence
    all_matches.sort(key=lambda x: x['confidence'], reverse=True)

    # Filter overlapping matches
    filtered_matches = []
    for match in all_matches:
        should_add = True
        for existing_match in filtered_matches:
            if get_overlap_area(match, existing_match) > 0.3:
                should_add = False
                break
        
        if should_add:
            filtered_matches.append(match)

    return filtered_matches

# Load and preprocess template
def load_and_preprocess_template(template_file: str, scale: float, angle: float) -> Optional[Tuple]:
    template = cv2.imread(template_file)
    if template is None:
        return None, (0, 0)
    
    # Resize
    width = int(template.shape[1] * scale)
    height = int(template.shape[0] * scale)

    if width == 0 or height == 0:
        return None, (0, 0)
        
    resized = cv2.resize(template, (width, height))

    # Rotate
    if angle != 0:
        matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1.0)
        rotated = cv2.warpAffine(resized, matrix, (width, height))
        return rotated, (width, height)
        
    return resized, (width, height)

# Check if a point in the image has map-like characteristics.
def is_valid_map_region(image: np.ndarray, center_point: Tuple) -> bool:
    x, y = center_point
    region_size = 8
    
    # Get region around point
    y_start = max(0, y - region_size)
    y_end = min(image.shape[0], y + region_size)
    x_start = max(0, x - region_size)
    x_end = min(image.shape[1], x + region_size)
    
    region = image[y_start:y_end, x_start:x_end]
    
    # Convert to HSV for better color detection
    hsv_region = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for white and blue
    lower_blue = np.array([85, 100, 200])
    upper_blue = np.array([130, 255, 255])
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    
    # Create masks
    blue_mask = np.all((hsv_region >= lower_blue) & (hsv_region <= upper_blue), axis=2)
    white_mask = np.all((hsv_region >= lower_white) & (hsv_region <= upper_white), axis=2)
    
    # Calculate percentage of matching pixels
    total_pixels = region_size * region_size * 4
    matching_pixels = np.sum(blue_mask | white_mask)
    
    return matching_pixels > (total_pixels * 0.08)

# Check for any overlap between matches
def get_overlap_area(rect1: Dict, rect2: Dict) -> float:
    x1, y1 = rect1['position']
    x2, y2 = rect2['position']
    w1, h1 = rect1['size']
    w2, h2 = rect2['size']

    # Calculate intersection
    intersection = max(0, min(x1 + w1, x2 + w2) - max(x1, x2)) * max(0, min(y1 + h1, y2 + h2) - max(y1, y2))

    # Return ratio relative to smaller rectangle
    return intersection / min(w1 * h1, w2 * h2)