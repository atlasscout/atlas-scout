import tkinter as tk
import win32gui

from settings.settings_manager import SettingsManager
from utils.logger import logger
from typing import Optional, Tuple


class TransparentOverlay:
    def __init__(self) -> None:
        # Load settings
        self.settings_manager = SettingsManager()

        # Main window
        self.root = tk.Tk()

        # Set window properties
        self.root.overrideredirect(True)
        self.root.attributes(
            '-topmost', True,           
            '-alpha', 1.0,              
            '-transparentcolor', 'black',
            '-disabled', False
        )
        

        # Canvas for drawing
        self.canvas = tk.Canvas(
            self.root,
            bg='black',
            highlightthickness=0,
            width=800,
            height=600,
            cursor='arrow'
        )
        self.canvas.pack(fill='both', expand=True)

        # Store elements grouped by their group IDs
        self.current_elements = {}
        self.next_group_id = 0

        self.canvas.bind('<Button-1>', self.on_click)

    # Remove group on click. group is (Rectangle, text and the close button)
    def on_click(self, event) -> None:
        # Find clicked items
        clicked_items = self.canvas.find_closest(event.x, event.y)
        if clicked_items:
            clicked_item = clicked_items[0]
            # Check if it's a close button
            tags = self.canvas.gettags(clicked_item)
            for tag in tags:
                if tag.startswith('close_'):
                    group_id = tag.split('_')[1]
                    self.remove_group(group_id)
                    break

    # Remove group
    def remove_group(self, group_id) -> None:
        if group_id in self.current_elements:
            for element in self.current_elements[group_id]:
                self.canvas.delete(element)
            del self.current_elements[group_id]

    # Position and size the overlay to match the game window
    def position_window(self, game_window_name: str = "Path of Exile 2") -> Optional[Tuple]:        
        try:
            # Find the game window
            hwnd = win32gui.FindWindow(None, game_window_name)
            if not hwnd:
                print(f"Window '{game_window_name}' not found")
                return None
            
            # Get window position and size
            rect = win32gui.GetWindowRect(hwnd)
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y
            
            # Force the window to be topmost and position it
            self.root.lift()
            self.root.attributes('-topmost', True)
            
            # Position overlay using exact coordinates from the game window
            self.root.geometry(f'{width}x{height}+{x}+{y}')
            
            # Ensure it stays on top
            self.root.update()
            
            return rect
            
        except Exception as e:
            logger.error(f"Error positioning overlay: {e}")
            return None 

    # Draw a map rectangle and label on the overlay
    def draw_map_info(self, x: int, y: int, width: int, height: int, text: str = "", color: str = "#ffffff") -> None:
        group_id = str(self.next_group_id)
        self.next_group_id += 1
        group_elements = []
        
        # Create rectangle
        rect = self.canvas.create_rectangle(
            x, y, x + width, y + height,
            outline=color,
            width=2,
            stipple='gray50',
            tags=f'group_{group_id}'
        )
        group_elements.append(rect)
        
        # Create close button
        button_size = 16
        button_x = x + width - button_size
        button_y = y
        
        # Close button background
        close_bg = self.canvas.create_oval(
            button_x, button_y,
            button_x + button_size, button_y + button_size,
            fill='white',
            outline=color,
            tags=(f'close_{group_id}', f'group_{group_id}')
        )
        
        # Close button X
        close_x = self.canvas.create_text(
            button_x + button_size/2,
            button_y + button_size/2,
            text='×',
            fill=color,
            font=('Segoe UI', 10, 'bold'),
            tags=(f'close_{group_id}', f'group_{group_id}')
        )
        
        group_elements.extend([close_bg, close_x])
        
        # Add text if provided
        if text:
            # Create background for text
            text_item = self.canvas.create_text(
                x, y - 5,
                text=text,
                fill=color,
                anchor='sw',
                font=('Segoe UI', 10, 'bold'),
                tags=f'group_{group_id}'
            )
            
            # Get text bounds
            bbox = self.canvas.bbox(text_item)
            if bbox:
                bg_rect = self.canvas.create_rectangle(
                    bbox[0] - 5,
                    bbox[1] - 5,
                    bbox[2] + 5,
                    bbox[3] + 5,
                    fill='white',
                    outline=color,
                    tags=f'group_{group_id}'
                )
                self.canvas.tag_lower(bg_rect, text_item)
                group_elements.extend([bg_rect, text_item])
            else:
                group_elements.append(text_item)
                
        self.current_elements[group_id] = group_elements

    # Clear/Remove elements from the overlay 
    def clear_overlay(self) -> None:
        for group_elements in self.current_elements.values():
            for element in group_elements:
                self.canvas.delete(element)
        self.current_elements.clear()

    # Update overlay with elements
    def update_overlay(self, matches) -> None:
        for match in matches:
            x, y = match['position']
            w, h = match['size']            
            
            # Prepare display text
            display_text = ""
            if all(key in match for key in ['map_name', 'biomes', 'layout', 'notes']):
                if match.get("is_favorite", False):
                    display_text += "⭐\n"
                display_text += f"Name: {match['map_name']}\n"
                if match['biomes'] != []: display_text += f"Biomes: {','.join(match['biomes'])}\n"                 
                display_text += f"Layout: {match['layout']}\n"
                if match['notes'] != None: display_text += f"Notes: {match['notes']}"
                
                # Check if hideout
                if match['layout'].lower() == 'hideout':
                    display_text += "This map is a hideout"

                # Add activities if present
                if 'activities' in match and match['activities']:
                    organized_features, contains_boss = self.settings_manager.get_features_display_text(match['activities'])                    
                    # Add each category of features
                    for display_name, features in organized_features.items():
                        display_text += f"\n{display_name}: {', '.join(features)}" 

                    # Check if the map contains boss
                    if contains_boss:
                        display_text += "\nMap contains Boss!"                          

            # Get color from match
            color = match.get('color', '#ffffff')
            
            if match.get('is_citadel', False):
                display_text = "⭐⭐⭐ CITADEL ⭐⭐⭐\n" + display_text

            self.draw_map_info(x, y, w, h, display_text, color)

    # Update the window
    def update(self) -> None:
        self.root.update()