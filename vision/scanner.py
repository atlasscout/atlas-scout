from .screenshot import get_window_screenshot
from controls.mouse_controller import MouseController
from .ocr import get_text_from_region
from .icon_detection import IconDetector
from .detection import find_maps
import time
import numpy as np
from typing import Any, List, Dict, Optional
from utils.logger import logger

class MapScanner:
    def __init__(self, transparent_overlay: Any, maps_data: List, favorite_maps: List, layout_colors: Dict, settings_manager: Any) -> None:
        self.transparent_overlay = transparent_overlay
        self.maps_data = maps_data
        self.favorite_maps = favorite_maps
        self.layout_colors = layout_colors    
        self.settings_manager = settings_manager    
        self.mouse_controller = MouseController()
        self.icon_detector = IconDetector()
        

    # Scan the currently hovered map
    def scan_hovered_map(self) -> List:
        screenshot, window_rect = get_window_screenshot()
        if screenshot is None or window_rect is None:
            logger.error(f"Failed to capture screenshot")
            return []
        
        curr_x, curr_y = self.mouse_controller.get_position()
        local_x = curr_x - window_rect[0]
        local_y = curr_y - window_rect[1]
        
        region_size = 30
        x = max(0, local_x - region_size)
        y = max(0, local_y - region_size)
        w = min(screenshot.shape[1] - x, region_size * 2)
        h = min(screenshot.shape[0] - y, region_size * 2)

        match = {
            'position': (int(x), int(y)),
            'size': (w, h)
        }

        processed_match = self.process_map(screenshot, match)                
        if processed_match:
            misc_settings = self.settings_manager.get_strategy_settings()           
            if misc_settings['misc']['apply_strategy_to_single']:
                return [processed_match] if self.should_include_match(processed_match) else []
            return [processed_match]
        return []

    # Scan Entier Screen
    def scan_screen(self) -> List:
        screenshot, window_rect = get_window_screenshot()
        if screenshot is None or window_rect is None:
            logger.error(f"Failed to capture screenshot")
            return []
        
        matches = find_maps(screenshot)
        if not matches:
            logger.warning(f"No map locations found")
            return []

        processed_matches = []
        for match in matches:           

            # Convert match position to screen coordinates
            screen_x = match['position'][0] + window_rect[0]
            screen_y = match['position'][1] + window_rect[1]

            # Move mouse to location center
            center_x = screen_x + match['size'][0] // 2
            center_y = screen_y + match['size'][1] // 2
            self.mouse_controller.move_to(center_x, center_y)

            # Wait for UI to appear
            time.sleep(0.2)

            # Take new screenshot for OCR and icon detection
            new_screenshot, _ = get_window_screenshot()
            if new_screenshot is not None:
                processed_match = self.process_map(new_screenshot, match)
                if processed_match:
                    if self.should_include_match(processed_match):
                        processed_matches.append(processed_match)

        return processed_matches

    # Process Map
    def process_map(self, screenshot: np.ndarray, match: Dict) -> Optional[Dict]:
       # Region to capture        
        x = match['position'][0]
        y = match['position'][1]
        w = match['size'][0]
        h =  match['size'][1]

        expand = 200
        y_start = y
        y_end = min(screenshot.shape[0], y + h + expand + 100)
        x_start = max(0, x - 400)
        x_end = min(screenshot.shape[1], x + w + expand + 400)
        
        region_img = screenshot[y_start:y_end, x_start:x_end]  
        

        # Get text and process region
        map_name, biomes, layout, notes = get_text_from_region(region_img, self.maps_data)        
        if map_name:            
            detected_icons = self.icon_detector.detect_icons(region_img)
            activities = [IconDetector.get_activity_name(icon) for icon in detected_icons]

            match['map_name'] = map_name
            match['is_citadel'] = "citadel" in map_name.lower()
            match['biomes'] = biomes
            match['layout'] = layout
            match['notes'] = notes
            match['is_favorite'] = map_name in self.favorite_maps
            match['color'] = self.layout_colors.get(layout, '#ffffff')
            match['activities'] = activities    
            return match
            
        return None
    
    # Check if the Map should be included in matches. (STRATEGY)
    def should_include_match(self, match: Dict) -> bool:
        strategy_settings = self.settings_manager.get_strategy_settings()
        endgame_activities = strategy_settings.get('endgame_activities', {})
        map_layouts = strategy_settings.get('map_layouts', {})
        misc_settings = strategy_settings.get('misc', {})

        must_contain_boss = misc_settings.get('contains_boss', False)
        if must_contain_boss:
            match_activities = match.get('activities', [])
            if 'Boss' not in match_activities:
                return False
        
        # Check if only favorites is enabled
        only_favorites = misc_settings.get('only_favorites', False)
        if only_favorites and not match.get('is_favorite', False):
            return False
        
        # Check map layout preferences
        any_layout_enabled = any(map_layouts.values())
        if any_layout_enabled:
            layout = match.get('layout')
            if not layout or not map_layouts.get(layout, False):
                return False

        # Check if any endgame activity strategy is enabled
        any_strategy_enabled = any(endgame_activities.values())
        
        # If no endgame activity strategy is enabled, include the match
        if not any_strategy_enabled:
            return True
            
        # If we have endgame strategies enabled, check if the match has any of them
        match_activities = match.get('activities', [])
        for activity, is_enabled in endgame_activities.items():
            if is_enabled and activity in match_activities:
                return True
                
        # If we have endgame strategies enabled but none match, exclude this match
        return False if any_strategy_enabled else True