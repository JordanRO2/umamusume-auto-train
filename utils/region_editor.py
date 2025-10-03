import cv2
import numpy as np
from PIL import ImageGrab
import json
from pathlib import Path
import time
from datetime import datetime
import utils.constants as constants
import pygetwindow as gw
import win32gui
import win32api
import win32con

class RegionEditor:
    """Interactive region editor with transparent overlay for real-time debugging"""

    def __init__(self):
        self.window_name = "Region Editor - Click and Drag to Edit"
        self.screen = None
        self.display_image = None
        self.original_image = None
        self.regions = {}
        self.selected_region = None
        self.dragging = False
        self.creating_new = False
        self.drag_start = None
        self.drag_type = None  # 'move', 'resize_tl', 'resize_br', 'resize_tr', 'resize_bl'
        self.new_region_start = None
        self.new_region_name = ""
        self.current_mouse = None
        self.scale = 1.0  # Start with full resolution
        self.show_coordinates = True
        self.regions_file = Path("debug_logs/custom_regions.json")
        self.overlay_mode = False  # Toggle between screenshot and overlay
        self.game_window = None
        self.window_offset = (0, 0)

        # Load existing regions from constants
        self.load_regions_from_constants()

        # Try to find game window
        self.find_game_window()

        # Colors for different region types
        self.colors = {
            "selected": (0, 255, 255),  # Yellow
            "normal": (0, 255, 0),      # Green
            "new": (255, 0, 255),        # Magenta
            "hover": (255, 255, 0),      # Cyan
        }

    def find_game_window(self):
        """Find the game window for overlay mode"""
        try:
            # Try to find Umamusume window
            windows = gw.getWindowsWithTitle("Umamusume")
            if windows:
                self.game_window = windows[0]
                self.window_offset = (self.game_window.left, self.game_window.top)
                print(f"[INFO] Found game window at ({self.game_window.left}, {self.game_window.top})")
                print(f"[INFO] Window size: {self.game_window.width}x{self.game_window.height}")
                return True

            # Try alternative window name from config
            import core.state as state
            if hasattr(state, 'WINDOW_NAME') and state.WINDOW_NAME:
                windows = gw.getWindowsWithTitle(state.WINDOW_NAME)
                if windows:
                    self.game_window = windows[0]
                    self.window_offset = (self.game_window.left, self.game_window.top)
                    print(f"[INFO] Found game window '{state.WINDOW_NAME}' at ({self.game_window.left}, {self.game_window.top})")
                    return True
        except Exception as e:
            print(f"[WARNING] Could not find game window: {e}")
            print("[INFO] Using fullscreen mode instead")

        return False

    def load_regions_from_constants(self):
        """Load regions from constants file"""
        self.regions = {
            "MOOD_REGION": constants.MOOD_REGION,
            "TURN_REGION": constants.TURN_REGION,
            "FAILURE_REGION": constants.FAILURE_REGION,
            "YEAR_REGION": constants.YEAR_REGION,
            "CRITERIA_REGION": constants.CRITERIA_REGION,
            "SKILL_PTS_REGION": constants.SKILL_PTS_REGION,
            "SCREEN_BOTTOM_REGION": constants.SCREEN_BOTTOM_REGION,
            "SCREEN_MIDDLE_REGION": constants.SCREEN_MIDDLE_REGION,
            "SCREEN_TOP_REGION": constants.SCREEN_TOP_REGION,
            "RACE_LIST_BOX_REGION": constants.RACE_LIST_BOX_REGION,
            "SUPPORT_CARD_ICON_BBOX": constants.SUPPORT_CARD_ICON_BBOX,
            "ENERGY_BBOX": constants.ENERGY_BBOX,
        }

        # Load custom regions if they exist
        if self.regions_file.exists():
            with open(self.regions_file, 'r') as f:
                custom = json.load(f)
                self.regions.update(custom)

    def save_custom_regions(self):
        """Save custom regions to file"""
        self.regions_file.parent.mkdir(exist_ok=True)

        # Filter out the original constants
        custom_regions = {k: v for k, v in self.regions.items()
                         if not k.endswith("_REGION") and not k.endswith("_BBOX")}

        with open(self.regions_file, 'w') as f:
            json.dump(custom_regions, f, indent=2)

        print("\n[SAVED] Custom regions saved to debug_logs/custom_regions.json")

    def capture_game_screen(self):
        """Capture the game screen at full resolution"""
        if self.game_window and not self.game_window.isMinimized:
            # Capture game window specifically
            bbox = (self.game_window.left, self.game_window.top,
                   self.game_window.left + self.game_window.width,
                   self.game_window.top + self.game_window.height)
            screen = ImageGrab.grab(bbox=bbox)
        else:
            # Capture full screen
            screen = ImageGrab.grab()

        return cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for region editing"""
        # Scale coordinates back to original if needed
        if self.scale != 1.0:
            x = int(x / self.scale)
            y = int(y / self.scale)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.handle_mouse_down(x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            self.handle_mouse_move(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.handle_mouse_up(x, y)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.handle_right_click(x, y)
        elif event == cv2.EVENT_MOUSEWHEEL:
            self.handle_mouse_wheel(flags)

    def handle_mouse_wheel(self, flags):
        """Handle mouse wheel for zooming"""
        if flags > 0:  # Scroll up - zoom in
            self.scale = min(2.0, self.scale + 0.1)
        else:  # Scroll down - zoom out
            self.scale = max(0.3, self.scale - 0.1)

        print(f"\r[ZOOM] Scale: {self.scale:.1f}x", end="", flush=True)
        self.update_display()

    def handle_mouse_down(self, x, y):
        """Handle mouse button press"""
        if self.creating_new:
            # Start creating new region
            self.new_region_start = (x, y)
            self.dragging = True
        else:
            # Check if clicking on an existing region
            for name, region in self.regions.items():
                rx, ry, rw, rh = self.convert_region(region)

                # Check corners for resize
                corner_size = 10
                if self.point_near(x, y, rx, ry, corner_size):
                    self.drag_type = 'resize_tl'
                    self.selected_region = name
                    self.dragging = True
                    self.drag_start = (x - rx, y - ry)
                    return
                elif self.point_near(x, y, rx + rw, ry, corner_size):
                    self.drag_type = 'resize_tr'
                    self.selected_region = name
                    self.dragging = True
                    self.drag_start = (x - (rx + rw), y - ry)
                    return
                elif self.point_near(x, y, rx, ry + rh, corner_size):
                    self.drag_type = 'resize_bl'
                    self.selected_region = name
                    self.dragging = True
                    self.drag_start = (x - rx, y - (ry + rh))
                    return
                elif self.point_near(x, y, rx + rw, ry + rh, corner_size):
                    self.drag_type = 'resize_br'
                    self.selected_region = name
                    self.dragging = True
                    self.drag_start = (x - (rx + rw), y - (ry + rh))
                    return

                # Check if inside region for move
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    self.drag_type = 'move'
                    self.selected_region = name
                    self.dragging = True
                    self.drag_start = (x - rx, y - ry)
                    return

    def handle_mouse_move(self, x, y):
        """Handle mouse movement"""
        if self.dragging:
            if self.creating_new and self.new_region_start:
                # Store current mouse position for preview
                self.current_mouse = (x, y)
                self.update_display()
            elif self.selected_region:
                rx, ry, rw, rh = self.convert_region(self.regions[self.selected_region])

                if self.drag_type == 'move':
                    # Move entire region
                    new_x = x - self.drag_start[0]
                    new_y = y - self.drag_start[1]
                    self.regions[self.selected_region] = (new_x, new_y, rw, rh)

                elif self.drag_type == 'resize_tl':
                    # Resize from top-left
                    new_x = x - self.drag_start[0]
                    new_y = y - self.drag_start[1]
                    new_w = rx + rw - new_x
                    new_h = ry + rh - new_y
                    if new_w > 10 and new_h > 10:
                        self.regions[self.selected_region] = (new_x, new_y, new_w, new_h)

                elif self.drag_type == 'resize_br':
                    # Resize from bottom-right
                    new_w = x - self.drag_start[0] - rx
                    new_h = y - self.drag_start[1] - ry
                    if new_w > 10 and new_h > 10:
                        self.regions[self.selected_region] = (rx, ry, new_w, new_h)

                elif self.drag_type == 'resize_tr':
                    # Resize from top-right
                    new_y = y - self.drag_start[1]
                    new_w = x - self.drag_start[0] - rx
                    new_h = ry + rh - new_y
                    if new_w > 10 and new_h > 10:
                        self.regions[self.selected_region] = (rx, new_y, new_w, new_h)

                elif self.drag_type == 'resize_bl':
                    # Resize from bottom-left
                    new_x = x - self.drag_start[0]
                    new_w = rx + rw - new_x
                    new_h = y - self.drag_start[1] - ry
                    if new_w > 10 and new_h > 10:
                        self.regions[self.selected_region] = (new_x, ry, new_w, new_h)

                self.update_display()
                self.print_region_info(self.selected_region)

    def handle_mouse_up(self, x, y):
        """Handle mouse button release"""
        if self.creating_new and self.new_region_start:
            # Finish creating new region
            x1, y1 = self.new_region_start
            x2, y2 = x, y

            # Normalize coordinates
            rx = min(x1, x2)
            ry = min(y1, y2)
            rw = abs(x2 - x1)
            rh = abs(y2 - y1)

            if rw > 10 and rh > 10:
                # Get name for new region
                name = input("\n[NEW REGION] Enter name for new region: ").strip()
                if name:
                    self.regions[name] = (rx, ry, rw, rh)
                    self.selected_region = name
                    print(f"\n[CREATED] New region '{name}': ({rx}, {ry}, {rw}, {rh})")
                    print(f"[COPY] {name} = ({rx}, {ry}, {rw}, {rh})")
                    self.save_custom_regions()

            self.new_region_start = None
            self.creating_new = False
            self.current_mouse = None

        self.dragging = False
        self.drag_type = None
        self.update_display()

    def handle_right_click(self, x, y):
        """Handle right click for context menu"""
        # Find region under cursor
        for name, region in self.regions.items():
            rx, ry, rw, rh = self.convert_region(region)
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                print(f"\n[RIGHT CLICK] Region: {name}")
                print(f"1. Delete region")
                print(f"2. Rename region")
                print(f"3. Copy region")
                choice = input("Enter choice (or press Enter to cancel): ").strip()

                if choice == "1":
                    if name not in ["MOOD_REGION", "TURN_REGION", "YEAR_REGION"]:  # Protect core regions
                        del self.regions[name]
                        print(f"[DELETED] Region '{name}' deleted")
                        self.save_custom_regions()
                    else:
                        print(f"[ERROR] Cannot delete core region '{name}'")

                elif choice == "2":
                    new_name = input(f"Enter new name for '{name}': ").strip()
                    if new_name and new_name not in self.regions:
                        self.regions[new_name] = self.regions.pop(name)
                        print(f"[RENAMED] '{name}' -> '{new_name}'")
                        self.save_custom_regions()

                elif choice == "3":
                    new_name = input(f"Enter name for copy of '{name}': ").strip()
                    if new_name and new_name not in self.regions:
                        self.regions[new_name] = region
                        print(f"[COPIED] '{name}' -> '{new_name}'")
                        self.save_custom_regions()

                self.update_display()
                return

    def convert_region(self, region):
        """Convert region to (x, y, width, height) format"""
        if len(region) == 4:
            x, y, w_or_x2, h_or_y2 = region
            if w_or_x2 > 500 and h_or_y2 > 500:  # Likely x2, y2
                return x, y, w_or_x2 - x, h_or_y2 - y
            else:
                return x, y, w_or_x2, h_or_y2
        return 0, 0, 100, 100

    def point_near(self, x1, y1, x2, y2, threshold):
        """Check if two points are near each other"""
        return abs(x1 - x2) <= threshold and abs(y1 - y2) <= threshold

    def update_display(self, capture_new=False):
        """Update the display with current regions"""
        if capture_new or self.original_image is None:
            self.original_image = self.capture_game_screen()

        self.display_image = self.original_image.copy()

        # Add semi-transparent overlay for better visibility
        overlay = self.display_image.copy()

        # Draw all regions
        for name, region in self.regions.items():
            rx, ry, rw, rh = self.convert_region(region)

            # Choose color and style
            if name == self.selected_region:
                color = self.colors["selected"]
                thickness = 3
                # Add semi-transparent fill for selected region
                cv2.rectangle(overlay, (rx, ry), (rx + rw, ry + rh), color, -1)
            else:
                color = self.colors["normal"]
                thickness = 2

            # Draw rectangle
            cv2.rectangle(self.display_image, (rx, ry), (rx + rw, ry + rh), color, thickness)

            # Draw corner handles for selected region
            if name == self.selected_region:
                handle_size = 8
                handle_color = (0, 255, 255)
                cv2.rectangle(self.display_image, (rx - handle_size//2, ry - handle_size//2),
                            (rx + handle_size//2, ry + handle_size//2), handle_color, -1)
                cv2.rectangle(self.display_image, (rx + rw - handle_size//2, ry - handle_size//2),
                            (rx + rw + handle_size//2, ry + handle_size//2), handle_color, -1)
                cv2.rectangle(self.display_image, (rx - handle_size//2, ry + rh - handle_size//2),
                            (rx + handle_size//2, ry + rh + handle_size//2), handle_color, -1)
                cv2.rectangle(self.display_image, (rx + rw - handle_size//2, ry + rh - handle_size//2),
                            (rx + rw + handle_size//2, ry + rh + handle_size//2), handle_color, -1)

            # Draw label
            label = f"{name}: ({rx},{ry},{rw},{rh})" if self.show_coordinates else name
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            label_y = ry - 5 if ry > 30 else ry + rh + 20

            # Background for text
            cv2.rectangle(self.display_image, (rx, label_y - text_size[1] - 4),
                         (rx + text_size[0] + 4, label_y + 4), (0, 0, 0), -1)
            cv2.putText(self.display_image, label, (rx + 2, label_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Apply overlay with transparency
        if self.selected_region:
            cv2.addWeighted(overlay, 0.2, self.display_image, 0.8, 0, self.display_image)

        # Draw new region being created
        if self.creating_new and self.new_region_start and self.current_mouse:
            x1, y1 = self.new_region_start
            x2, y2 = self.current_mouse
            # Normalize coordinates
            rx = min(x1, x2)
            ry = min(y1, y2)
            rw = abs(x2 - x1)
            rh = abs(y2 - y1)
            cv2.rectangle(self.display_image, (rx, ry), (rx + rw, ry + rh), self.colors["new"], 2)
            # Show size while creating
            label = f"New: ({rx},{ry},{rw},{rh})"
            cv2.putText(self.display_image, label, (rx, ry - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors["new"], 1)

        # Scale for display if needed
        if self.scale != 1.0:
            height, width = self.display_image.shape[:2]
            new_width = int(width * self.scale)
            new_height = int(height * self.scale)
            scaled = cv2.resize(self.display_image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            cv2.imshow(self.window_name, scaled)
        else:
            cv2.imshow(self.window_name, self.display_image)

    def print_region_info(self, name):
        """Print region information to console"""
        if name in self.regions:
            region = self.regions[name]
            x, y, w, h = self.convert_region(region)
            print(f"\r[REGION] {name} = ({x}, {y}, {w}, {h})    ", end="", flush=True)

    def print_all_regions(self):
        """Print all regions to console"""
        print("\n" + "="*80)
        print("CURRENT REGIONS (Copy these to update your constants.py):")
        print("="*80)

        for name, region in sorted(self.regions.items()):
            x, y, w, h = self.convert_region(region)
            print(f"{name} = ({x}, {y}, {w}, {h})")

        print("="*80 + "\n")

    def run(self):
        """Run the region editor"""
        print("\n" + "="*80)
        print("REGION EDITOR - Interactive Mode")
        print("="*80)
        print("\nCONTROLS:")
        print("  - Left Click & Drag: Move or resize regions")
        print("  - Right Click: Context menu (delete/rename/copy)")
        print("  - Mouse Wheel: Zoom in/out")
        print("  - 'n': Create new region")
        print("  - 'p': Print all regions to console")
        print("  - 's': Save custom regions")
        print("  - 'c': Toggle coordinate display")
        print("  - 'r': Refresh screen capture")
        print("  - 'f': Toggle fullscreen")
        print("  - '+/-': Increase/decrease scale")
        print("  - 'h': Show this help")
        print("  - 'q' or ESC: Quit")
        print("\nDrag corners to resize, drag center to move regions")
        print(f"\n[INFO] Current scale: {self.scale:.1f}x (use mouse wheel to zoom)")
        print("="*80 + "\n")

        # Capture initial screen
        self.original_image = self.capture_game_screen()
        self.display_image = self.original_image.copy()

        # Create window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        # Set initial window size
        height, width = self.original_image.shape[:2]
        if width > 1920 or height > 1080:
            # Scale down large screens for initial display
            self.scale = min(1920 / width, 1080 / height)
            cv2.resizeWindow(self.window_name, int(width * self.scale), int(height * self.scale))
        else:
            cv2.resizeWindow(self.window_name, width, height)

        # Initial display
        self.update_display()

        # Auto-refresh timer
        last_refresh = time.time()
        auto_refresh_interval = 5.0  # Refresh every 5 seconds

        while True:
            key = cv2.waitKey(30) & 0xFF  # 30ms delay for smoother response

            # Auto-refresh periodically
            if time.time() - last_refresh > auto_refresh_interval:
                self.update_display(capture_new=True)
                last_refresh = time.time()

            if key == ord('q') or key == 27:  # q or ESC
                break

            elif key == ord('n'):  # New region
                self.creating_new = True
                print("\n[NEW] Click and drag to create new region...")

            elif key == ord('p'):  # Print all
                self.print_all_regions()

            elif key == ord('s'):  # Save
                self.save_custom_regions()
                self.print_all_regions()

            elif key == ord('c'):  # Toggle coordinates
                self.show_coordinates = not self.show_coordinates
                self.update_display()
                print(f"\n[DISPLAY] Coordinates {'ON' if self.show_coordinates else 'OFF'}")

            elif key == ord('r'):  # Refresh screen
                print("\n[REFRESH] Capturing new screenshot...")
                self.update_display(capture_new=True)

            elif key == ord('f'):  # Toggle fullscreen
                # Get current window state and toggle
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN,
                                    cv2.WINDOW_FULLSCREEN if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN) == cv2.WINDOW_NORMAL else cv2.WINDOW_NORMAL)

            elif key == ord('+') or key == ord('='):  # Zoom in
                self.scale = min(2.0, self.scale + 0.1)
                print(f"\r[ZOOM] Scale: {self.scale:.1f}x", end="", flush=True)
                self.update_display()

            elif key == ord('-') or key == ord('_'):  # Zoom out
                self.scale = max(0.3, self.scale - 0.1)
                print(f"\r[ZOOM] Scale: {self.scale:.1f}x", end="", flush=True)
                self.update_display()

            elif key == ord('h'):  # Help
                print("\nCONTROLS:")
                print("  - Left Click & Drag: Move or resize regions")
                print("  - Right Click: Context menu")
                print("  - Mouse Wheel: Zoom in/out")
                print("  - 'n': Create new region")
                print("  - 'p': Print all regions")
                print("  - 's': Save custom regions")
                print("  - 'c': Toggle coordinates")
                print("  - 'r': Refresh screen")
                print("  - 'f': Toggle fullscreen")
                print("  - '+/-': Zoom in/out")
                print("  - 'q': Quit")

            elif ord('1') <= key <= ord('9'):  # Quick select regions 1-9
                idx = key - ord('1')
                names = list(self.regions.keys())
                if idx < len(names):
                    self.selected_region = names[idx]
                    self.update_display()
                    self.print_region_info(self.selected_region)

        cv2.destroyAllWindows()

        # Final output
        self.print_all_regions()
        print("\n[EXIT] Region editor closed")
        print("[TIP] Copy the region definitions above to update your constants.py file")

def main():
    """Run the region editor standalone"""
    editor = RegionEditor()
    editor.run()

if __name__ == "__main__":
    main()