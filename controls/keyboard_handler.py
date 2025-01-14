import keyboard
import time
from settings.settings_manager import SettingsManager
from utils.logger import logger

class KeyboardHandler:    
    def __init__(self) -> None:
        self.last_key_press = 0
        self.key_cooldown = 0.5
        self.settings_manager = SettingsManager()
        self.keybinds = self.settings_manager.settings.get('keybinds', {})

        # Default keybinds as fallback
        self.default_keybinds = {
            "scan_all": "alt+1",
            "scan_hovered": "alt+2",
            "clear_overlay": "alt+3",
            "toggle_window": "alt+s",
            "exit": "alt+esc"
        }

    # Check which action has been pressed
    def check_action(self, action: str) -> bool:
        current_time = time.time()

        key = self.keybinds.get(action)
        if not key:
            logger.warning(f"No keybind found for action: {action}")
            return False

        if keyboard.is_pressed(key) and (current_time - self.last_key_press) >= self.key_cooldown:
            self.last_key_press = current_time
            return True
        return False