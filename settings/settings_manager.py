import json
import os
from utils.logger import logger
from typing import List, Dict, Optional, Tuple

class SettingsManager:

    def __init__(self) -> None:
        # Load Maps on Init        
        self.settings_file_path = 'data/settings.json'
        self.settings = self.load_settings()

        self.maps_file_path = 'data/maps.json'
        self.maps = self.load_maps()

        self.maps_features_file_path = 'data/maps_features.json'
        self.maps_features = self.load_maps_features()

    # Handle Maps
    def load_maps(self) -> List:
        try:
            if os.path.exists(self.maps_file_path):
                with open(self.maps_file_path, 'r') as f:
                    data = json.load(f)
                    return data['maps']
        except Exception as e:
            logger.error(f"Error loading maps: {e}")           
        return []
    
    def get_maps(self) -> List:
        return self.maps
    
    def get_favorite_maps(self) -> List:
        return self.settings['favorite_maps']


    # Handle Strategy
    def get_strategy_settings(self) -> List:
        return self.settings['strategy']

    # Handle Settings
    def load_settings(self) -> Dict:
        try:
            if os.path.exists(self.settings_file_path):
                with open(self.settings_file_path, 'r') as f:
                    settings = json.load(f)
                    self.settings = settings
                    return settings
        except Exception as e:            
            logger.error(f"Error loading settings: {e}") 
        return {}
    
    def save_settings(self, settings: Dict) -> bool:
        try:
            with open(self.settings_file_path, "w") as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}") 
            return False
        

    # Handle Map Features
    def load_maps_features(self) -> Dict:
        try:
            if os.path.exists(self.maps_features_file_path):
                with open(self.maps_features_file_path, 'r') as f:
                    maps_features = json.load(f)
                    return maps_features
        except Exception as e:            
            print (f"Error loading maps features: {e}")
        return {}

    def get_feature_category(self, feature_name: str) -> Optional[str]:
        for category, data in self.maps_features.get('features', {}).items():
            if feature_name in data.get('items', {}):
                return category
        return None

    def get_features_display_text(self, feature_names: List) -> Tuple:
        organized_features = {}
        contains_boss = False
                
        for feature in feature_names:
            if feature == "Boss":
                contains_boss = True
            else:
                category = self.get_feature_category(feature)
                if category:
                    category_data = self.maps_features['features'][category]
                    display_name = category_data['display_name']
                    
                    if display_name not in organized_features:
                        organized_features[display_name] = []
                    
                    # Get the display text for this specific feature
                    feature_text = category_data['items'][feature]
                    organized_features[display_name].append(feature_text)           
        
        return organized_features, contains_boss


    # Handle Colors
    def get_colors(self) -> Dict:
        return self.settings['colors']
    

