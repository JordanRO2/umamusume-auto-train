# Interactive Region Editor Documentation

## Overview
The Region Editor is a powerful real-time tool for editing, creating, and testing search regions while the bot is running. All changes are displayed in real-time with coordinates printed to console for easy copying.

## Features

### 1. **Real-Time Visual Editing**
- See all regions overlaid on actual game screenshot
- Drag to move regions
- Drag corners to resize
- Visual feedback with color coding
- Resizable window for better viewing

### 2. **Interactive Controls**
- **Mouse-based editing** - Click and drag interface
- **Real-time coordinate output** - See changes instantly in console
- **Context menus** - Right-click for additional options
- **Keyboard shortcuts** - Quick access to common functions

### 3. **Region Management**
- Create new regions on the fly
- Delete unwanted regions
- Rename regions for clarity
- Duplicate regions as templates
- Save/load custom regions

## Usage

### Starting the Editor

#### Method 1: Hotkey (During Bot Runtime)
```
Press F4 while bot is running
```
The bot will pause automatically while editor is open.

#### Method 2: Standalone Test Script
```bash
python test_region_editor.py
```

#### Method 3: Direct Import
```python
from utils.region_editor import RegionEditor
editor = RegionEditor()
editor.run()
```

## Controls

### Mouse Controls

| Action | Description |
|--------|-------------|
| **Left Click + Drag (Center)** | Move entire region |
| **Left Click + Drag (Corners)** | Resize region from that corner |
| **Right Click** | Open context menu for region |
| **Click Empty Space** | Deselect current region |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `n` | Start creating new region (then drag) |
| `p` | Print all regions to console |
| `s` | Save custom regions to file |
| `c` | Toggle coordinate display |
| `r` | Refresh screen capture |
| `h` | Show help |
| `1-9` | Quick select regions |
| `q/ESC` | Quit editor |

## Creating New Regions

1. Press `n` to enter creation mode
2. Click and drag to draw the new region
3. Release mouse button
4. Enter a name when prompted
5. The console will show:
```
[CREATED] New region 'MY_CUSTOM_REGION': (450, 300, 200, 150)
[COPY] MY_CUSTOM_REGION = (450, 300, 200, 150)
```

## Real-Time Console Output

As you edit regions, the console shows live coordinates:
```
[REGION] MOOD_REGION = (705, 125, 130, 25)
[REGION] TURN_REGION = (260, 65, 110, 75)
[REGION] MY_CUSTOM = (450, 300, 200, 150)
```

Press `p` to print all regions formatted for copying:
```
================================================================================
CURRENT REGIONS (Copy these to update your constants.py):
================================================================================
MOOD_REGION = (705, 125, 130, 25)
TURN_REGION = (260, 65, 110, 75)
FAILURE_REGION = (250, 770, 560, 65)
MY_CUSTOM_REGION = (450, 300, 200, 150)
================================================================================
```

## Applying Changes

### Temporary (Current Session)
Custom regions are automatically available to the bot during the current session.

### Permanent (Update Constants)

1. Copy the output from pressing `p` in the editor
2. Open `utils/constants.py`
3. Replace or add the region definitions:
```python
# Original
MOOD_REGION = (705, 125, 130, 25)

# Updated (your new values)
MOOD_REGION = (710, 120, 135, 30)

# New custom region
MY_CUSTOM_REGION = (450, 300, 200, 150)
```

## Custom Regions File

Custom regions are saved to: `debug_logs/custom_regions.json`

Example content:
```json
{
  "CUSTOM_BUTTON": [450, 300, 200, 50],
  "SPECIAL_AREA": [100, 200, 300, 400],
  "NEW_ZONE": [500, 600, 150, 100]
}
```

## Visual Indicators

### Region Colors
- **Green**: Normal region
- **Yellow/Cyan**: Selected region
- **Magenta**: New region being created
- **Yellow Squares**: Resize handles on selected region

### Display Options
- Coordinates can be toggled on/off with `c`
- Window is fully resizable
- Scale adjusts automatically

## Tips & Best Practices

### 1. **Test Before Saving**
- Edit regions while bot is running to see immediate effects
- Use F4 to quickly open editor during debugging

### 2. **Naming Conventions**
- Use descriptive names: `SKILL_BUTTON_REGION`
- Keep consistent suffixes: `_REGION`, `_BBOX`, `_AREA`
- Use CAPS_SNAKE_CASE for constants

### 3. **Coordinate Formats**
The editor outputs in `(x, y, width, height)` format:
```python
# Standard format used by the bot
REGION = (x_position, y_position, width, height)
```

### 4. **Quick Workflow**
1. Press F4 to open editor
2. Adjust regions by dragging
3. Press `p` to get coordinates
4. Copy to constants.py
5. Press `q` to close and resume bot

### 5. **Backup Original Values**
Before editing core regions, save the original values:
```python
# Backup
MOOD_REGION_ORIGINAL = (705, 125, 130, 25)
# New
MOOD_REGION = (710, 120, 135, 30)
```

## Integration with Debug Mode

The region editor works seamlessly with debug mode:

```bash
# Run bot with debug mode
python main.py --debug

# Press F4 anytime to edit regions
# Changes apply immediately to searches
```

## Troubleshooting

### Issue: Region not updating in bot
- Make sure to save with `s` in editor
- Restart bot if you updated constants.py
- Check that region name matches exactly

### Issue: Can't select small regions
- Zoom in by resizing the editor window
- Use number keys (1-9) for quick selection
- Increase region size temporarily for editing

### Issue: Wrong coordinates after editing
- Press `r` to refresh the screen capture
- Make sure game window hasn't moved
- Check if window offset is applied correctly

## Example Session

```
1. Start bot: python main.py --debug
2. Press F4 when you want to edit
3. Editor opens with current screen

[EDITOR] Opening region editor...
[EDITOR] Bot will pause while editor is open

4. Drag MOOD_REGION to new position
[REGION] MOOD_REGION = (710, 120, 135, 30)

5. Press 'n' to create new region
[NEW] Click and drag to create new region...
[CREATED] New region 'SPECIAL_BUTTON': (850, 450, 100, 40)

6. Press 'p' to print all
================================================================================
CURRENT REGIONS (Copy these to update your constants.py):
================================================================================
MOOD_REGION = (710, 120, 135, 30)
SPECIAL_BUTTON = (850, 450, 100, 40)
================================================================================

7. Press 's' to save
[SAVED] Custom regions saved to debug_logs/custom_regions.json

8. Press 'q' to close
[EXIT] Region editor closed
[EDITOR] Editor closed, bot resumed
```

## Advanced Features

### Batch Region Creation
Create multiple regions quickly:
1. Press `n`, create region, name it
2. Immediately press `n` again for next region
3. Continue until all regions created
4. Press `p` to get all coordinates at once

### Region Templates
Use right-click → "Copy region" to duplicate existing regions as templates for similar areas.

### Fine-Tuning
Hold Shift (if implemented) for slower, more precise movement when dragging.