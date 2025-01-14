import glob
import os
import cv2
import numpy as np
from utils.logger import logger
from typing import List

class IconDetector:
    def __init__(self, icons_dir: str = 'data/icons') -> None:
        self.icons_dir = icons_dir
        self.icons = {}
        self.load_icons()

    # Load all icon templates from the icons directory
    def load_icons(self) -> None:
        icon_files = glob.glob(os.path.join(self.icons_dir, '*.png'))
        for icon_file in icon_files:
            icon_name = os.path.splitext(os.path.basename(icon_file))[0]
            icon_template = cv2.imread(icon_file, cv2.IMREAD_COLOR)
            if icon_template is not None:
                self.icons[icon_name] = icon_template
            else:
                logger.error(f'Failed to load icon: {icon_file}')

    # Using Template Matching to detect icons
    def detect_icons(self, region_img: np.ndarray, threshold: float = 0.85) -> List:
        detected_icons = []        
        for icon_name, template in self.icons.items(): 
            result = cv2.matchTemplate(region_img, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)               
            if len(locations[0]) > 0:
                detected_icons.append(icon_name)            
        return detected_icons
    
    # Get Activity Name from Icon Filename
    def get_activity_name(icon_name: str) -> str:
        activity_map = {
            'breach': 'Breach',
            'boss': 'Boss',
            'corruption': 'Corruption',
            'hideout': 'Hideout',
            'delirium': 'Delirium',
            'irradiated': 'Irradiated',
            'ritual': 'Ritual',
            'expedition': 'Expedition',
        }
        return activity_map.get(icon_name, icon_name.title())