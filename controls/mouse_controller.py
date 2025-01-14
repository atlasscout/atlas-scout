import win32api
import time
from utils.logger import logger
from typing import Tuple

class MouseController:
    def __init__(self) -> None:
        self.original_pos = win32api.GetCursorPos()

    # Get current mouse position
    def get_position(self) -> Tuple:
        return win32api.GetCursorPos()    
    
    # Move mouse to specific coords
    def move_to(self, x: int, y: int, smooth: bool = True) -> bool:
        try:
            if smooth:
                curr_x, curr_y = win32api.GetCursorPos()
                steps = 20
                x_step = (x - curr_x) / steps
                y_step = (y - curr_y) / steps
                
                for i in range(steps):
                    new_x = int(curr_x + (x_step * (i + 1)))
                    new_y = int(curr_y + (y_step * (i + 1)))
                    win32api.SetCursorPos((new_x, new_y))
                    time.sleep(0.01)
            else:
                win32api.SetCursorPos((x, y))

            return True
        except Exception as e:
            logger.error(f"Failed to move mouse to ({x}, {y}): {e}")
            return False
