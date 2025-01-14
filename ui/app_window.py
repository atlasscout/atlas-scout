import tkinter as tk
import customtkinter as ctk
from settings.settings_manager import SettingsManager
from .maps_table import MapsTable
from .color_picker import ColorPicker
from utils.logger import logger



class AppWindow:

    def __init__(self) -> None:
        # Load settings
        self.settings_manager = SettingsManager()

        # customtkinter config
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main Window        
        self.root = ctk.CTk()
        self.root.title = "Atlas Scout"

        # Set window properties
        self.root.overrideredirect(True)
        self.root.attributes(
            '-topmost', True,           
            '-alpha', 0.98,              
        )
        
        # Position window
        self.position_window()

        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Title Bar
        self.create_title_bar()

        # Tabview
        self.create_tabview()

        # Visibility Flag
        self.visible = False


    # Position Window
    def position_window(self) -> None:   
        window_width = 400
        window_height = 500       
        screen_height = self.root.winfo_screenheight()
        x_position = 20
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Create a custom title bar
    def create_title_bar(self) -> None:
        title_bar = ctk.CTkFrame(self.main_frame)
        title_bar.pack(fill=tk.X, padx=2, pady=2)
        
        title_label = ctk.CTkLabel(
            title_bar,
            text="Atlas Scout",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Bind dragging events
        title_bar.bind('<Button-1>', self.start_move)
        title_bar.bind('<B1-Motion>', self.on_move)

    # Create Tabview
    def create_tabview(self) -> None:
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add needed tabs
        self.tabview.add("Controls")
        self.tabview.add("Maps")
        self.tabview.add("Strategy")
        self.tabview.add("Colors")

        # Setup the tabs
        self.setup_tab_controls()
        self.setup_tab_maps()
        self.setup_tab_strategy()
        self.setup_tab_colors()


    # Setup Tabs --- Controls
    def setup_tab_controls(self) -> None:
        controls_frame = ctk.CTkFrame(self.tabview.tab("Controls"), fg_color="transparent")
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Add title
        controls_label = ctk.CTkLabel(
            controls_frame,
            text="Controls",
            font=("Segoe UI", 14, "bold")
        )
        controls_label.pack(anchor=tk.W, padx=5, pady=(0, 10))

        # Get keybinds from settings
        keybinds = self.settings_manager.settings.get('keybinds', {})

        # Create a frame for each keybind
        for action, key in keybinds.items():            
            bind_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
            bind_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Format the action name for display
            display_name = action.replace('_', ' ').title()
            
            # Add the control label
            label = ctk.CTkLabel(
                bind_frame,
                text=f"{display_name}:",
                font=("Segoe UI", 12)
            )
            label.pack(side=tk.LEFT)
            
            # Add the keybind in a rectangle (similar to color hex display)
            value = ctk.CTkEntry(
                bind_frame,
                width=80,
                font=("Segoe UI", 12)
            )
            value.insert(0, key)
            value.configure(state="readonly")
            value.pack(side=tk.RIGHT, padx=5)

        # Add note about changing keybinds
        note_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        note_frame.pack(fill=tk.X, padx=5, pady=(20, 0))
        
        note_label = ctk.CTkLabel(
            note_frame,
            text="Note: To change these keybinds, update the settings.json file in the data folder.",
            font=("Segoe UI", 11),
            wraplength=350,
            justify="left"
        )
        note_label.pack(anchor=tk.W)

    # Setup Tabs --- Maps
    def setup_tab_maps(self) -> None:
        maps_frame = ctk.CTkFrame(self.tabview.tab("Maps"))
        maps_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Get maps and favorite maps
        maps = self.settings_manager.get_maps()
        favorite_maps = self.settings_manager.get_favorite_maps()
        
        # Create the Maps Table
        self.maps_table = MapsTable(
            maps_frame,
            maps, 
            favorite_maps,
            self.on_favourite_changed
        )
        self.maps_table.pack(fill=tk.BOTH, expand=True)

    def on_favourite_changed(self, map_name: str, is_favorite: bool) -> None:
        try:
            current_settings = self.settings_manager.settings.copy()
            favorite_maps = current_settings.get('favorite_maps', [])

            if is_favorite and map_name not in favorite_maps:
                favorite_maps.append(map_name)
            elif not is_favorite and map_name in favorite_maps:
                favorite_maps.remove(map_name)

            current_settings['favorite_maps'] = favorite_maps
            if self.settings_manager.save_settings(current_settings):
                logger.info(f"Updated favorite status for {map_name}")
            else:
                logger.error(f"Failed to save favorite status for {map_name}")
                # Refresh table to revert changes
                self.maps_table.refresh_favorites(self.settings_manager.get_favorite_maps())

        except Exception as e:            
            logger.error(f'Error updating favourites: {e}')
            self.maps_table.refresh_favorites(self.settings_manager.get_favorite_maps())


    # Setup Tabs --- Strategy
    def setup_tab_strategy(self) -> None:
        container_frame = ctk.CTkFrame(self.tabview.tab("Strategy"), fg_color="transparent")
        container_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollable frame for content
        strategy_frame = ctk.CTkScrollableFrame(
            container_frame,
            label_text="",
        )
        strategy_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Get current strategy settings
        strategy_settings = self.settings_manager.get_strategy_settings()
        endgame_activities = strategy_settings.get('endgame_activities', {})
        map_layouts = strategy_settings.get('map_layouts', {})
        misc_settings = strategy_settings.get('misc', {})

        # Create variables for checkboxes
        self.activity_vars = {}
        self.layout_vars = {}

        ## Map Features / Categories
        # Create Frame for each Category
        features = self.settings_manager.maps_features.get('features', {})
        for category, data in features.items():
            # Create category frame
            category_frame = ctk.CTkFrame(strategy_frame)
            category_frame.pack(fill=tk.X, pady=(0, 1), padx=5)
            
            # Add category label
            category_label = ctk.CTkLabel(
                category_frame,
                text=data['display_name'],
                font=("Segoe UI", 14, "bold")
            )
            category_label.pack(anchor=tk.W, padx=5, pady=(5, 5))



             # Create frame for grid layout
            grid_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
            grid_frame.pack(fill=tk.X, padx=5, pady=2)

            # Keep track of grid positions
            row = 0
            col = 0

            # Add checkboxes for each item in the category
            for feature_name in sorted(data['items'].keys()):
                if category == 'map_layout':
                    saved_state = map_layouts.get(feature_name, False)
                    var = tk.BooleanVar(value=saved_state)
                    self.layout_vars[feature_name] = var
                else:
                    saved_state = endgame_activities.get(feature_name, False)
                    var = tk.BooleanVar(value=saved_state)
                    self.activity_vars[feature_name] = var
                
                checkbox = ctk.CTkCheckBox(
                    grid_frame,
                    text=data['items'][feature_name],
                    variable=var,
                    command=self.save_strategy_settings,
                    font=("Segoe UI", 12)
                )
                # Place checkbox in grid
                checkbox.grid(row=row, column=col, sticky="w", padx=5, pady=2)
                
                # Update column and row positions
                col += 1
                if col >= 3:  # Move to next row after 3 columns
                    col = 0
                    row += 1

        ## Misc
        misc_frame = ctk.CTkFrame(strategy_frame)
        misc_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        misc_label = ctk.CTkLabel(
            misc_frame,
            text="Misc",
            font=("Segoe UI", 14, "bold")
        )
        misc_label.pack(anchor=tk.W, padx=5, pady=(5, 5))

        saved_favorites_state = misc_settings.get('only_favorites', False)        
        self.only_favorites_var = tk.BooleanVar(value=saved_favorites_state)
        favorites_checkbox = ctk.CTkCheckBox(
            misc_frame,
            text="Only favorite maps!",
            variable=self.only_favorites_var,
            command=self.save_strategy_settings,
            font=("Segoe UI", 12)
        )
        favorites_checkbox.pack(anchor=tk.W, padx=5, pady=2)

        contains_boss_state = misc_settings.get('contains_boss', False)
        self.contains_boss_var = tk.BooleanVar(value=contains_boss_state)
        boss_checkbox = ctk.CTkCheckBox(
            misc_frame,
            text="Must contains boss!",
            variable=self.contains_boss_var,
            command=self.save_strategy_settings,
            font=("Segoe UI", 12)
        )
        boss_checkbox.pack(anchor=tk.W, padx=5, pady=2)

        apply_to_single_state = misc_settings.get('apply_strategy_to_single', False)
        self.apply_to_single_var = tk.BooleanVar(value=apply_to_single_state)
        appt_to_single_checkbox = ctk.CTkCheckBox(
            misc_frame,
            text="Apply strategy to Single-Map Lookup",
            variable=self.apply_to_single_var,
            command=self.save_strategy_settings,
            font=("Segoe UI", 12)
        )
        appt_to_single_checkbox.pack(anchor=tk.W, padx=5, pady=2)

    def save_strategy_settings(self) -> None:
        try:
            current_settings = self.settings_manager.settings.copy()
            current_settings['strategy'] = {
                'endgame_activities': {
                    activity: var.get()
                    for activity, var in self.activity_vars.items()
                },
                'map_layouts': {
                    layout: var.get()
                    for layout, var in self.layout_vars.items()
                },
                'misc': {
                    'only_favorites': self.only_favorites_var.get(),
                    'contains_boss': self.contains_boss_var.get(),
                    'apply_strategy_to_single': self.apply_to_single_var.get()
                }
            }
            if self.settings_manager.save_settings(current_settings):
                self.settings_manager.settings = current_settings
                logger.info("Strategy settings saved successfully")
            else:                
                logger.error("Failed to save strategy settings")
        except Exception as e:            
            logger.error(f'Error saving strategy settigns: {e}')


    # Setup Tabs -- Colors
    def setup_tab_colors(self) -> None:
        colors_frame = ctk.CTkFrame(self.tabview.tab("Colors"), fg_color="transparent")
        colors_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        colors_label = ctk.CTkLabel(
            colors_frame,
            text="Layout Colors",
            font=("Segoe UI", 14, "bold")
        )
        colors_label.pack(anchor=tk.W, padx=5, pady=(0, 10))

        saved_colors = self.settings_manager.get_colors()
        self.layout_colors = {
            layout: ColorPicker(
                colors_frame, 
                layout, 
                color, 
                on_change=self.save_colors
            )
            for layout, color in saved_colors.items()
        }

    def save_colors(self) -> None:
        try:
            current_settings = self.settings_manager.settings.copy()
            colors = {
                layout: picker.get_color()
                for layout, picker in self.layout_colors.items()
            }
            current_settings['colors'] = colors
            if self.settings_manager.save_settings(current_settings):
                logger.info("Colors settings saved successfully")
            else:
                logger.error("Failed to save colors settings")
        except Exception as e:
            logger.error(f"Error saving colors: {e}")

    # Handle Window Dragging
    def start_move(self, event) -> None:
        self.x = event.x
        self.y = event.y

    def on_move(self, event) -> None:
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    
    # Handle Visibility
    def toggle_visibility(self) -> None:
        if self.visible:
            self.root.withdraw()
        else:
            self.root.deiconify()
        self.visible = not self.visible
    
    def hide_app(self) -> None:
        self.visible = False
        self.root.withdraw()        

    # Update the window
    def update(self) -> None:
        self.root.update()