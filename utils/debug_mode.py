import cv2
import numpy as np
from PIL import ImageGrab, Image, ImageDraw, ImageFont
import threading
import time
from datetime import datetime
import os
from pathlib import Path
from utils.log import info, debug, warning
import utils.constants as constants

# Debug flags
DEBUG_MODE = False
STEP_BY_STEP = False
SHOW_SEARCH_ZONES = False
DEBUG_OVERLAY = None
DEBUG_LOCK = threading.Lock()
STEP_CONTINUE = threading.Event()
OVERLAY_THREAD = None
LOG_FILE = None
LOG_DIR = Path("debug_logs")

def setup_logging():
    """Setup debug logging to file"""
    global LOG_FILE, LOG_DIR

    # Create debug logs directory
    LOG_DIR.mkdir(exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = LOG_DIR / f"debug_{timestamp}.log"
    LOG_FILE = open(log_filename, 'w', encoding='utf-8')

    log_message(f"Debug logging started at {datetime.now()}")
    log_message(f"Log file: {log_filename}")

    return log_filename

def log_message(message, level="INFO"):
    """Write message to debug log file"""
    global LOG_FILE
    if LOG_FILE and not LOG_FILE.closed:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        LOG_FILE.write(f"[{timestamp}] [{level}] {message}\n")
        LOG_FILE.flush()

def close_logging():
    """Close the debug log file"""
    global LOG_FILE
    if LOG_FILE and not LOG_FILE.closed:
        log_message("Debug logging ended")
        LOG_FILE.close()

def enable_debug_mode(show_zones=True, step_mode=True):
    """Enable debug mode with optional features"""
    global DEBUG_MODE, SHOW_SEARCH_ZONES, STEP_BY_STEP
    DEBUG_MODE = True
    SHOW_SEARCH_ZONES = show_zones
    STEP_BY_STEP = step_mode

    if STEP_BY_STEP:
        STEP_CONTINUE.set()  # Initialize as ready to continue

    # Setup logging
    log_file = setup_logging()

    info(f"Debug mode enabled - Log: {log_file}")
    info(f"- Show search zones: {SHOW_SEARCH_ZONES}")
    info(f"- Step-by-step mode: {STEP_BY_STEP}")

    log_message("Debug mode configuration:")
    log_message(f"  Show zones: {SHOW_SEARCH_ZONES}")
    log_message(f"  Step mode: {STEP_BY_STEP}")

    # Don't automatically start overlay - let user control it
    if SHOW_SEARCH_ZONES:
        info("Zone visualization enabled (will show inline, not as overlay)")

def disable_debug_mode():
    """Disable debug mode"""
    global DEBUG_MODE, SHOW_SEARCH_ZONES, STEP_BY_STEP, OVERLAY_THREAD
    DEBUG_MODE = False
    SHOW_SEARCH_ZONES = False
    STEP_BY_STEP = False

    # Close any open windows
    cv2.destroyAllWindows()

    log_message("Debug mode disabled")
    close_logging()
    info("Debug mode disabled")

def wait_for_step():
    """Wait for user to press Enter to continue (for step-by-step debugging)"""
    if not STEP_BY_STEP or not DEBUG_MODE:
        return

    STEP_CONTINUE.clear()
    print("\n[DEBUG] Press Enter to continue to next step...")
    log_message("Waiting for user input (step mode)")
    input()
    log_message("User continued execution")
    STEP_CONTINUE.set()

def draw_search_zone(image, region, name="", color=(255, 0, 0), thickness=2):
    """Draw a rectangle on the image to show search zone"""
    if not DEBUG_MODE or not SHOW_SEARCH_ZONES:
        return image

    # Handle different region formats
    if isinstance(region, tuple):
        if len(region) == 4:
            # Format: (x, y, width, height) or (x1, y1, x2, y2)
            x, y, w_or_x2, h_or_y2 = region

            # Determine if it's width/height or x2/y2
            if w_or_x2 > 200 and h_or_y2 > 200:  # Likely x2, y2
                x1, y1, x2, y2 = x, y, w_or_x2, h_or_y2
            else:  # Likely width, height
                x1, y1, x2, y2 = x, y, x + w_or_x2, y + h_or_y2
        else:
            return image
    else:
        return image

    # Convert PIL Image to OpenCV format if needed
    if isinstance(image, Image.Image):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Draw rectangle
    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)

    # Add label if provided
    if name:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        text_size = cv2.getTextSize(name, font, font_scale, font_thickness)[0]

        # Position text above the rectangle
        text_x = int(x1)
        text_y = int(y1) - 5 if y1 > 20 else int(y2) + 15

        # Draw background for text
        cv2.rectangle(image,
                     (text_x - 2, text_y - text_size[1] - 2),
                     (text_x + text_size[0] + 2, text_y + 2),
                     (255, 255, 255), -1)

        # Draw text
        cv2.putText(image, name, (text_x, text_y), font, font_scale, color, font_thickness)

    return image

def save_debug_screenshot(image, name="debug"):
    """Save a debug screenshot to file"""
    if not DEBUG_MODE:
        return

    timestamp = datetime.now().strftime("%H%M%S")
    filename = LOG_DIR / f"{name}_{timestamp}.png"

    if isinstance(image, np.ndarray):
        cv2.imwrite(str(filename), image)
    else:
        image.save(filename)

    log_message(f"Saved screenshot: {filename}")
    return filename

def visualize_all_zones(save_to_file=False, show_window=False):
    """Capture screen and draw all search zones"""
    if not DEBUG_MODE:
        return None

    try:
        # Capture screen
        screen = ImageGrab.grab()
        image = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

        # Define zones to visualize
        zones = {
            "MOOD": constants.MOOD_REGION,
            "TURN": constants.TURN_REGION,
            "FAILURE": constants.FAILURE_REGION,
            "YEAR": constants.YEAR_REGION,
            "CRITERIA": constants.CRITERIA_REGION,
            "SKILL_PTS": constants.SKILL_PTS_REGION,
            "BOTTOM_SCREEN": constants.SCREEN_BOTTOM_REGION,
            "MIDDLE_SCREEN": constants.SCREEN_MIDDLE_REGION,
            "TOP_SCREEN": constants.SCREEN_TOP_REGION,
            "SUPPORT_CARD": constants.SUPPORT_CARD_ICON_BBOX,
            "ENERGY": constants.ENERGY_BBOX,
            "RACE_LIST": constants.RACE_LIST_BOX_REGION,
        }

        # Define colors for different zone types
        colors = {
            "MOOD": (0, 255, 0),      # Green
            "TURN": (0, 255, 0),      # Green
            "YEAR": (0, 255, 0),      # Green
            "CRITERIA": (0, 255, 0),   # Green
            "FAILURE": (255, 0, 0),    # Red
            "SKILL_PTS": (255, 255, 0), # Yellow
            "BOTTOM_SCREEN": (255, 0, 255), # Magenta
            "MIDDLE_SCREEN": (255, 128, 0), # Orange
            "TOP_SCREEN": (0, 255, 255),    # Cyan
            "SUPPORT_CARD": (128, 0, 255),  # Purple
            "ENERGY": (0, 128, 255),        # Light Blue
            "RACE_LIST": (255, 0, 128),     # Pink
        }

        # Draw all zones
        for name, region in zones.items():
            color = colors.get(name, (255, 0, 0))
            image = draw_search_zone(image, region, name, color)
            log_message(f"Zone {name}: {region}")

        if save_to_file:
            save_debug_screenshot(image, "all_zones")

        if show_window:
            # Show in a non-blocking way with timeout
            height, width = image.shape[:2]
            scale = 0.5  # Scale down to 50%
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv2.resize(image, (new_width, new_height))

            cv2.imshow("Debug: Search Zones", resized)
            cv2.waitKey(1)  # Non-blocking, just refresh

        return image
    except Exception as e:
        log_message(f"Error in visualize_all_zones: {e}", "ERROR")
        warning(f"Failed to visualize zones: {e}")
        return None

def show_debug_info(template_path=None, region=None, threshold=None, matches=None, save_screenshot=False):
    """Display and log debug information for current search operation"""
    if not DEBUG_MODE:
        return

    # Build debug message
    debug_msg = []
    debug_msg.append("="*60)
    debug_msg.append("Search Operation")

    if template_path:
        debug_msg.append(f"Template: {template_path}")
    if region:
        debug_msg.append(f"Region: {region}")
    if threshold is not None:
        debug_msg.append(f"Threshold: {threshold}")
    if matches is not None:
        if isinstance(matches, list):
            debug_msg.append(f"Matches found: {len(matches)}")
            for i, match in enumerate(matches[:5]):  # Show first 5 matches
                debug_msg.append(f"  Match {i+1}: {match}")
        else:
            debug_msg.append(f"Match result: {matches}")

    debug_msg.append("="*60)

    # Log to file
    for line in debug_msg:
        log_message(line)

    # Print to console (but don't block)
    if STEP_BY_STEP:
        print("\n".join(debug_msg))
        wait_for_step()

def log_search_attempt(action, region=None, success=False, details=""):
    """Log search attempts for debugging"""
    if not DEBUG_MODE:
        return

    status = "SUCCESS" if success else "FAILED"
    timestamp = time.strftime("%H:%M:%S")

    log_entry = f"[{timestamp}] {status} - {action}"
    if region:
        log_entry += f" | Region: {region}"
    if details:
        log_entry += f" | {details}"

    log_message(log_entry)

    # Also write to separate search log
    with DEBUG_LOCK:
        with open(LOG_DIR / "search_history.log", "a") as f:
            f.write(log_entry + "\n")

# Enhanced template matching with debug support
def debug_match_template(template_path, region=None, threshold=0.85, original_func=None):
    """Wrapper for match_template with debug visualization"""
    if not DEBUG_MODE:
        return original_func(template_path, region, threshold) if original_func else []

    log_message(f"Starting template match: {template_path}")

    # Show search info before search
    show_debug_info(template_path=template_path, region=region, threshold=threshold)

    # Perform original search
    result = original_func(template_path, region, threshold) if original_func else []

    # Log results
    log_message(f"Match complete: {len(result)} matches found")

    # Show results
    show_debug_info(matches=result)

    # Save screenshot if matches found
    if SHOW_SEARCH_ZONES and result and len(result) > 0:
        try:
            screen = ImageGrab.grab()
            image = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

            for match in result:
                x, y, w, h = match
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, "FOUND", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            save_debug_screenshot(image, f"match_{Path(template_path).stem}")
        except Exception as e:
            log_message(f"Error saving match screenshot: {e}", "ERROR")

    return result

def cleanup_old_logs(keep_last_n=10):
    """Clean up old debug logs, keeping only the last N"""
    try:
        log_files = sorted(LOG_DIR.glob("debug_*.log"))
        if len(log_files) > keep_last_n:
            for log_file in log_files[:-keep_last_n]:
                log_file.unlink()
                info(f"Deleted old log: {log_file}")
    except Exception as e:
        warning(f"Error cleaning up logs: {e}")