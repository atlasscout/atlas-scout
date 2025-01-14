import win32gui
import mss
import numpy as np
import cv2
from utils.logger import logger
from typing import Tuple

def get_window_screenshot(window_name: str = "Path of Exile 2") -> Tuple:    
    try:
        hwnd = win32gui.FindWindow(None, window_name)
        if not hwnd:            
            logger.error(f"Window '{window_name}' not found")
            return None, None
            
        # Get window position and size
        rect = win32gui.GetWindowRect(hwnd)
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        
        # Capture screenshot using mss
        with mss.mss() as sct:
            monitor = {"top": y1, "left": x1, "width": width, "height": height}
            screenshot = sct.grab(monitor)

            # Convert screenshot to a numpy array
            screenshot_np = np.array(screenshot)

            # Convert from BGRA to BGR (OpenCV format)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_BGRA2BGR)            

            return screenshot_bgr, rect
        
    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}")
        return None, None