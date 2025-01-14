from tkinter import ttk
from typing import List, Dict, Any

class MapsTable(ttk.Frame):
    def __init__(self, parent, maps: List, favorite_maps: List, on_favorite_changed) -> None:
        super().__init__(parent, style='Dark.TFrame')
        
        # Store callback and data
        self.on_favorite_changed = on_favorite_changed
        self.maps = maps
        self.favorite_maps = favorite_maps
        
        # Sorting state
        self.sort_column = 'Name'  # Default sort column
        self.sort_reverse = False   # Default ascending
        
        # Create treeview
        self.tree = ttk.Treeview(self, columns=('Name', 'Biomes', 'Layout', 'Favorite'), show='headings', style='Dark.Treeview')
        
        # Configure scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure columns with sorting
        for col in ('Name', 'Biomes', 'Layout', 'Favorite'):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
        
        # Set column widths
        self.tree.column('Name', width=100)
        self.tree.column('Biomes', width=100)  # Increased width for list display
        self.tree.column('Layout', width=100)
        self.tree.column('Favorite', width=70)
        
        # Initial population and sort
        self.populate_table()
        
        # Bind click event for favorite toggle
        self.tree.bind('<ButtonRelease-1>', self.on_click)
        
        # Pack widgets
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    # Format biomes list into a readable string.
    def format_biomes(self, biomes: List) -> str:
        return ', '.join(sorted(biomes))

    # Get the appropriate sort key based on the column.
    def get_sort_key(self, item: Dict, column: str) -> Any:        
        if column == 'Biomes':
            # Sort by the first biome, or empty string if no biomes
            biomes = item[column]
            return sorted(biomes)[0] if biomes else ''
        elif column == 'Favorite':
            return item['_is_favorite']
        else:
            return item[column]

    # Clear and repopulate the table with current data
    def populate_table(self) -> None:        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Prepare data for sorting
        table_data = []
        for loc in self.maps:
            is_favorite = loc['name'] in self.favorite_maps
            table_data.append({
                'Name': loc['name'],
                'Biomes': loc['biomes'], 
                'Layout': loc['layout'],
                'Favorite': '★' if is_favorite else '☆',
                '_is_favorite': is_favorite  # Hidden field for sorting
            })
        
        # Sort data
        table_data.sort(
            key=lambda x: self.get_sort_key(x, self.sort_column),
            reverse=self.sort_reverse
        )
        
        # Insert sorted data
        for item in table_data:
            self.tree.insert('', 'end', values=(
                item['Name'],
                self.format_biomes(item['Biomes']),  # Format list for display
                item['Layout'],
                item['Favorite']
            ))

    # Sort table by specified column
    def sort_by_column(self, column: str) -> None:        
        if self.sort_column == column:
            # If already sorting by this column, reverse the order
            self.sort_reverse = not self.sort_reverse
        else:
            # New column, set as sort column and default to ascending
            self.sort_column = column
            self.sort_reverse = False
        
        # Update sort indicators in headers
        for col in ('Name', 'Biomes', 'Layout', 'Favorite'):
            if col == self.sort_column:
                indicator = "▼" if self.sort_reverse else "▲"
                self.tree.heading(col, text=f"{col} {indicator}")
            else:
                self.tree.heading(col, text=col)
        
        # Repopulate with new sort
        self.populate_table()
    
    # Handle click event
    def on_click(self, event) -> None:
        region = self.tree.identify_region(event.x, event.y)
        if region == 'cell':
            column = self.tree.identify_column(event.x)
            if column == '#4':  # Favorite column
                item = self.tree.identify_row(event.y)
                if item:
                    values = self.tree.item(item)['values']
                    if values:
                        map_name = values[0]
                        is_favorite = values[3] == '★'
                        # Toggle favorite
                        new_favorite = not is_favorite
                        self.tree.set(item, 'Favorite', '★' if new_favorite else '☆')
                        # Notify callback
                        self.on_favorite_changed(map_name, new_favorite)
    
    # Refresh the favorite status of all maps
    def refresh_favorites(self, favorite_maps: List) -> None:
        self.favorite_maps = favorite_maps
        self.populate_table()  # Repopulate to maintain sort order