import tkinter as tk
import customtkinter as ctk
from tkinter import colorchooser

class ColorPicker:
    def __init__(self, parent, label: str, initial_color: str = "#FFFFFF", on_change=None)  -> None:
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.pack(fill=tk.BOTH, padx=5, pady=2)
        
        # Store callback
        self.on_change = on_change
        
        # Label
        self.label = ctk.CTkLabel(
            self.frame, 
            text=f"{label}:",
            font=("Segoe UI", 12)
        )
        self.label.pack(side=tk.LEFT)
        
        # Color display and button
        self.color_var = tk.StringVar(value=initial_color)
        
        # Create custom button that shows the color
        self.color_button = ctk.CTkButton(
            self.frame,
            text="",
            width=30,
            height=20,
            fg_color=initial_color,
            command=self.choose_color
        )
        self.color_button.pack(side=tk.RIGHT, padx=5)
        
        # Entry for hex color
        self.color_entry = ctk.CTkEntry(
            self.frame,
            textvariable=self.color_var,
            width=80,
            font=("Segoe UI", 12)
        )
        self.color_entry.pack(side=tk.RIGHT, padx=5)
        
        # Bind entry changes to update button color
        self.color_var.trace('w', self.on_color_change)

    # Open color chooser dialog and update color        
    def choose_color(self) -> None:
        color = colorchooser.askcolor(color=self.color_var.get())
        if color[1]:  # If color was chosen (not cancelled)
            self.color_var.set(color[1])
    
    # Handle color changes from either the entry or color picker
    def on_color_change(self, *args) -> None:
        try:
            color = self.color_var.get()
            if color.startswith('#') and len(color) in [4, 7]:
                self.color_button.configure(fg_color=color)
                # Notify callback if provided
                if self.on_change:
                    self.on_change()
        except tk.TclError:
            pass  # Invalid color format
    
    # Get current color value
    def get_color(self) -> str:        
        return self.color_var.get()