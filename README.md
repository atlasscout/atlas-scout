# Atlas Scout

A tool for Path of Exile 2 that helps identify and analyze maps on the Atlas.

## Core Features

- **Automatic Atlas Scanning**: Scans the entire visible screen of the Atlas to detect and analyze visible and available maps.
- **Individual Map Scanning**: Analyze single maps. (Manual Scanning)
- **Advanced Filtering**: Apply strategy-based filtering and favorite maps system to both scanning modes.
- **Customizable Colors**: Assign different colors to map layouts (Linear, Maze, Open, Hideout) for better visibility.

## Atlas Scout in action
- Automatic Scanning
https://github.com/user-attachments/assets/00f063ff-e555-4440-849a-9b6686d8392a

- Automatic Scanning with Strategy
https://github.com/user-attachments/assets/eb9fc6c1-2bca-4f49-b9dd-73924128e8f5

- Manual Scanning
https://github.com/user-attachments/assets/d88984a6-6a0f-460a-9bc2-b55777652e98

- Manual Scanning with Strategy
https://github.com/user-attachments/assets/92bdc728-a7f3-48ef-8e73-ff2b3f2105d4

- Colors
https://github.com/user-attachments/assets/b222a630-92ed-4fd6-85c1-1e8b0572ae71

- Favorite Maps
https://github.com/user-attachments/assets/d542fb41-a821-4aa7-b010-f2a7f09f3b13

## IMPORTANT NOTE

Some people mentioned that if the mouse automatically moves around, then this is **bannable** by GGG, I dont know how accurate this is but please be aware. If you want to use the tool without the automatic mouse movement, then dont use the Automatic Scan. You can still use the manual scan and achieve the same thing.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/atlasscout/atlas-scout.git
cd atlas-scout
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

3. Install required packages:
```bash
python -m pip install -r requirements.txt
```

4. Install Tesseract OCR and update the path in `settings.json` 

## Configuration (settings.json)

The `settings.json` file controls the tool's behavior:

```json
{
    "keybinds": {
        "scan_all": "alt+1",        # Scan entire Atlas
        "scan_hovered": "alt+2",    # Scan single map
        "clear_overlay": "alt+3",   # Clear all highlights
        "toggle_window": "alt+s",   # Show/hide settings
        "exit": "alt+esc"           # Exit application
    },    
    "settings": {
        "refs_folder" : "data/refs/1080p/*.png", # Path of the templates folder.
        "scales": [0.9, 1.0, 1.1],  # Template matching scales
        "rotations": [0],           # Template matching rotations
        "tesseract_cmd_location": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    }, 
    # Other settings in json...
}
```

Key configuration options:
- **Keybinds**: Customize keyboard shortcuts for all actions. 
- **Settings**: Adjust detection parameters and Tesseract path.
- **Other Settings**: Other settings are used to store Colors, Strategy and Favourite Maps.

5. Run the tool
```bash
python main.py
```

## Very Important: Map Detection (PLEASE READ)

Atlas Scout uses OpenCV's template matching algorithm to detect maps. Here's what you need to know:

### How Template Matching Works

- The tool compares reference images (templates) against the game screen
- Each template is scaled and rotated according to the settings

### Detection Challenges and Solutions

| Issue | Problem | Solution |
|-------|---------|----------|
| Resolution Dependency | Detection accuracy depends on screen resolution matching reference images | Enable multi-scaling by adding more scale values in settings.json. Note: This will affect scanning speed |
| Partially Obstructed Maps | Maps covered by effects or UI elements may not be detected | Take screenshots of these maps and add them to the refs folder. When similar layouts appear later, they'll be detected |
| Atlas Zoom Level | Scanner may fail to detect maps when Atlas is zoomed in | Enable multi-scaling or add specific reference images for zoomed-in maps |
| Screen Edge Overlays | Map information may not be detected when overlay appears near screen edges | Currently investigating better solutions for this issue |

### Important Notes

1. **Adding Custom References**
   - You can add your own reference images in `data/refs/<resolution>/`
   - Simply take a screenshot of the map only and place it in the folder
   - If you have enough images, you can set the default scale to [1.0] in settings.json to disable multi-scaling.
   - Check existing images in refs folder for examples

2. **Multi-scaling Configuration**
   - Update settings.json to add more scale options
   - Example configuration:
     ```json
     "scales": [0.8, 0.9, 1.0, 1.1, 1.2]
     ```

3. **Quick Screenshot Tip**
   - Use Windows shortcut `SHIFT + Windows Key + S`
   - Highlight the map area only
   - Save the screenshot in the refs folder

4. **Tools still in development**
Please keep in mind that the tool is still in development and you will face some issues and bugs.

### Important Note on Map Detection
Currently, I am using template matching to detect maps on the screen which can be very straightforward and fast. The problem is that maps can have different layouts on the atlas, some are covered by other entities, some have structures near/on them etc., so this is making template matching harder than it should be. Because of all of this, some maps won't be detected at all (especially the ones that are almost completely hidden). In the section below you will read more about how to improve the accuracy of detection. Finally, I am working on a better method for map detection. Currently, I have a trained ML model that is detecting maps with good accuracy. Once I'm done training and fine-tuning it, I'll add it into the tool.
