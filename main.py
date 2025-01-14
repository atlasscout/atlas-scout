from ui.app_window import AppWindow
from ui.transparent_overlay import TransparentOverlay
from controls.keyboard_handler import KeyboardHandler
from vision.scanner import MapScanner
import time

def main():
    print("App is running...")
   
    app_window = AppWindow()
    transparent_overlay = TransparentOverlay()    
    keyboard_handler = KeyboardHandler()

    while True:
        # Handle Exit/Quit
        if keyboard_handler.check_action("exit"):
            print("ALT+ESC pressed - Exiting...")
            break

        # Handle Toggle App Window
        if keyboard_handler.check_action("toggle_window"):
            app_window.toggle_visibility()

        # Load Settings and Prepare Scanner
        settings_manager = app_window.settings_manager
        settings_manager.load_settings()
        scanner = MapScanner(
            transparent_overlay,
            settings_manager.get_maps(),
            settings_manager.get_favorite_maps(),
            settings_manager.get_colors(),
            settings_manager          
        )        
        
        # Handle Full Scan
        if keyboard_handler.check_action("scan_all"):            
            app_window.hide_app()            
            transparent_overlay.clear_overlay()
            transparent_overlay.position_window()
            matches = scanner.scan_screen()
            if matches:
                transparent_overlay.update_overlay(matches)

        # Handle Scanning Single Map
        if keyboard_handler.check_action("scan_hovered"):
            app_window.hide_app()
            # transparent_overlay.clear_overlay()
            transparent_overlay.position_window()
            matches = scanner.scan_hovered_map()
            if matches:
                transparent_overlay.update_overlay(matches)       


        # Handle Clear Overlay
        if keyboard_handler.check_action("clear_overlay"):
            transparent_overlay.clear_overlay()
        
        app_window.update()
        transparent_overlay.update()
        # Small sleep to prevent high CPU usage
        time.sleep(0.01)

if __name__ == "__main__":
    main()
        