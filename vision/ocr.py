import cv2
import pytesseract
from utils.logger import logger
import numpy as np
from typing import List, Tuple
from settings.settings_manager import SettingsManager


settings_manager = SettingsManager()
settings = settings_manager.settings.get('settings', {})
tesseract_cmd_location = settings.get('tesseract_cmd_location', '')

# Set Tesserac path
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_location

def get_text_from_region(region_img: np.ndarray, maps_data: List) -> Tuple:
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
        
        # Thresholding to improve text detection
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # OCR with improved configuration
        text = pytesseract.image_to_string(
            thresh,
            config='--psm 11 --oem 3'
        ).strip()      
        
        # Validate against known locations
        return validate_map(text, maps_data)
        
    except Exception as e:
        logger.error(f'Error in text recognition: {e}')
        return None, None, None, None
    

def validate_map(text: str, maps_data: List) -> Tuple:
    if not text:
        return None, None, None, None
    
    # Clean the input text
    cleaned_text = text.strip().lower()   

    # Split text and compare
    words = cleaned_text.split("\n")

    for map in maps_data:
        if map['name'].lower() in words:
            return map['name'], map['biomes'], map['layout'], map['notes'] 
    
    return None, None, None, None