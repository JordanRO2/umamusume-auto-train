# Debug Mode Documentation - Non-Blocking Version

## Overview
The debug mode provides comprehensive logging and visualization for troubleshooting without blocking the bot's operation. All visualizations are saved to files and all operations are logged.

## Key Features

### 1. Non-Blocking Operation
- **No popup windows** that block execution
- All visualizations saved as PNG files in `debug_logs/`
- Timestamped screenshots for each search operation
- Continuous operation with logging

### 2. Comprehensive File Logging
- Detailed logs saved to `debug_logs/debug_YYYYMMDD_HHMMSS.log`
- Separate search history in `debug_logs/search_history.log`
- Automatic screenshots of matches and search zones
- Log rotation (keeps last 10 logs by default)

### 3. Step-by-Step Debugging
- Optional pause after each operation
- Press Enter to continue to next step
- All visualizations still saved to files
- Perfect for understanding bot flow

## File Structure

```
debug_logs/
├── debug_20240101_120000.log      # Main debug log
├── search_history.log             # Search operations log
├── all_zones_120030.png          # Zone visualization
├── search_next_btn_120035.png    # Search region screenshot
├── found_next_btn_120036.png     # Match result screenshot
└── multi_search_results_120040.png # Multi-search results
```

## Usage

### Command Line Arguments
```bash
# Enable debug mode with logging only
python main.py --debug

# Enable step-by-step debugging
python main.py --step

# Both modes together
python main.py --debug --step
```

### Hotkeys (During Runtime)
- **F1**: Start/Stop bot (default)
- **F2**: Toggle debug mode on/off
- **F3**: Toggle step-by-step mode on/off

### Testing
```bash
# Run the test suite
python test_debug.py

# Options:
# 1. Test logging system
# 2. Test zone visualization (saves to file)
# 3. Test search with logging
# 4. Test non-blocking step mode
# 5. View log files
# 6. Clean up old logs
```

## Log File Format

### Main Debug Log (`debug_YYYYMMDD_HHMMSS.log`)
```
[12:34:56.789] [INFO] Debug logging started at 2024-01-01 12:34:56
[12:34:56.790] [INFO] Debug mode configuration:
[12:34:56.790] [INFO]   Show zones: True
[12:34:56.790] [INFO]   Step mode: False
[12:34:57.123] [INFO] match_template called: assets/buttons/next_btn.png, region=(125, 800, 875, 280), threshold=0.85
[12:34:57.456] [INFO] Found 1 matches (before dedup: 1)
[12:34:57.457] [INFO] Saved screenshot: debug_logs/found_next_btn_123457.png
```

### Search History Log (`search_history.log`)
```
[12:34:57] SUCCESS - match_template: assets/buttons/next_btn.png | Region: (125, 800, 875, 280) | Found 1 matches
[12:35:02] FAILED - match_template: assets/buttons/cancel_btn.png | Region: None | No matches
[12:35:10] SUCCESS - multi_match: event | Found 2 matches
```

## Debug Information Captured

### For Each Search Operation:
1. **Template path** being searched
2. **Search region** coordinates
3. **Confidence threshold** used
4. **Number of matches** found
5. **Match coordinates** (first 5)
6. **Screenshot** of search area
7. **Screenshot** of matches found

### For Each Click Operation:
1. **Target** (image or coordinates)
2. **Click position** (x, y)
3. **Success/failure** status
4. **Associated text/description**

### Zone Visualizations:
- Saved every 30 seconds during operation
- Manual save via test script
- Color-coded regions with labels
- Full screen capture with overlays

## Performance Considerations

### Minimal Impact Mode (Logging Only):
```bash
python main.py --debug
```
- Only logs to files
- No screenshots saved
- Minimal performance impact
- Good for production debugging

### Full Debug Mode (With Screenshots):
```bash
python main.py --debug --step
```
- Saves screenshots of all operations
- Creates zone visualizations
- Higher disk usage
- Best for detailed troubleshooting

## Troubleshooting Guide

### Issue: Bot not finding expected elements
1. Enable debug mode: `python main.py --debug`
2. Check `debug_logs/` for search screenshots
3. Review `search_history.log` for failed searches
4. Verify regions in zone visualization images

### Issue: Wrong click positions
1. Enable step mode: `python main.py --step`
2. Watch console output for click coordinates
3. Check screenshots for actual vs expected positions

### Issue: Unexpected bot behavior
1. Enable full debug: `python main.py --debug --step`
2. Step through each operation
3. Review main debug log for decision flow
4. Check saved screenshots for visual confirmation

## Log Management

### Automatic Cleanup:
- Keeps last 10 debug logs by default
- Run `python test_debug.py` and select option 6 to clean manually
- Old screenshots are not automatically deleted

### Manual Review:
```bash
# View latest log
tail -f debug_logs/debug_*.log

# Search for errors
grep ERROR debug_logs/debug_*.log

# View search failures
grep FAILED debug_logs/search_history.log
```

## Zone Color Reference

| Zone | Color | RGB | Purpose |
|------|-------|-----|---------|
| MOOD/TURN/YEAR | Green | (0, 255, 0) | Status indicators |
| FAILURE | Red | (255, 0, 0) | Failure rate display |
| SKILL_PTS | Yellow | (255, 255, 0) | Skill points |
| BOTTOM_SCREEN | Magenta | (255, 0, 255) | Bottom UI area |
| MIDDLE_SCREEN | Orange | (255, 128, 0) | Middle content |
| TOP_SCREEN | Cyan | (0, 255, 255) | Top UI area |
| SUPPORT_CARD | Purple | (128, 0, 255) | Support cards |
| ENERGY | Light Blue | (0, 128, 255) | Energy bar |
| RACE_LIST | Pink | (255, 0, 128) | Race selection |

## Tips

1. **Start with logging only** to identify issues without performance impact
2. **Use step mode** when you need to understand the exact sequence
3. **Check screenshots** in `debug_logs/` to visually confirm searches
4. **Review logs after bot stops** for post-mortem analysis
5. **Clean up old logs periodically** to save disk space

## Example Debug Session

```bash
# 1. Start bot with debug mode
python main.py --debug

# 2. Let it run for a few cycles
# (Bot runs normally, logging to files)

# 3. Stop bot (F1)

# 4. Review logs
python test_debug.py
# Select option 5 to view logs

# 5. Check specific issues in screenshots
ls debug_logs/*.png

# 6. Clean up when done
python test_debug.py
# Select option 6 to clean old logs
```