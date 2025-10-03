import cv2
import numpy as np
from PIL import ImageGrab
import threading
import time
import json
from pathlib import Path
from collections import deque
from datetime import datetime
import queue

class DebugVisualizer:
    """Real-time debug visualization with resizable windows"""

    def __init__(self):
        self.running = False
        self.windows = {}
        self.window_configs = {}
        self.update_queue = queue.Queue()
        self.visualizer_thread = None
        self.config_file = Path("debug_logs/window_config.json")
        self.last_images = {}
        self.fps = 30  # Target FPS for smooth updates

        # Load saved window configurations
        self.load_window_configs()

    def load_window_configs(self):
        """Load saved window positions and sizes"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.window_configs = json.load(f)
            except:
                self.window_configs = {}

    def save_window_configs(self):
        """Save current window positions and sizes"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.window_configs, f, indent=2)

    def start(self):
        """Start the visualization thread"""
        if self.running:
            return

        self.running = True
        self.visualizer_thread = threading.Thread(target=self._visualizer_loop, daemon=True)
        self.visualizer_thread.start()
        print("[DEBUG] Real-time visualizer started")

    def stop(self):
        """Stop the visualization thread"""
        self.running = False
        if self.visualizer_thread:
            self.visualizer_thread.join(timeout=1)

        # Save window configurations
        self.save_window_configs()

        # Close all windows
        cv2.destroyAllWindows()
        print("[DEBUG] Real-time visualizer stopped")

    def _visualizer_loop(self):
        """Main visualization loop running in separate thread"""
        frame_time = 1.0 / self.fps

        while self.running:
            start_time = time.time()

            try:
                # Process all pending updates
                while not self.update_queue.empty():
                    try:
                        update = self.update_queue.get_nowait()
                        self._process_update(update)
                    except queue.Empty:
                        break

                # Refresh existing windows
                for window_name, image in self.last_images.items():
                    if window_name in self.windows:
                        cv2.imshow(window_name, image)

                # Handle window events and check for closed windows
                key = cv2.waitKey(1) & 0xFF

                # Check for 'q' to close individual windows
                if key == ord('q'):
                    # Close the currently focused window
                    pass

                # Check for 'r' to reset window positions
                if key == ord('r'):
                    self.reset_windows()

                # Save window positions periodically
                if hasattr(self, '_last_save') and time.time() - self._last_save > 5:
                    self._update_window_configs()
                    self.save_window_configs()
                    self._last_save = time.time()
                elif not hasattr(self, '_last_save'):
                    self._last_save = time.time()

            except Exception as e:
                print(f"[DEBUG] Visualizer error: {e}")

            # Maintain target FPS
            elapsed = time.time() - start_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

    def _process_update(self, update):
        """Process a visualization update"""
        window_name = update['window']
        image = update['image']
        resize = update.get('resize', True)

        # Create or update window
        if window_name not in self.windows:
            self._create_window(window_name)

        # Apply resize if needed
        if resize and window_name in self.window_configs:
            config = self.window_configs[window_name]
            if 'width' in config and 'height' in config:
                image = cv2.resize(image, (config['width'], config['height']))

        # Store for refresh
        self.last_images[window_name] = image

        # Show image
        cv2.imshow(window_name, image)

    def _create_window(self, window_name):
        """Create a new resizable window"""
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        self.windows[window_name] = True

        # Apply saved configuration if exists
        if window_name in self.window_configs:
            config = self.window_configs[window_name]
            if 'x' in config and 'y' in config:
                cv2.moveWindow(window_name, config['x'], config['y'])
            if 'width' in config and 'height' in config:
                cv2.resizeWindow(window_name, config['width'], config['height'])
        else:
            # Default size and position
            if window_name == "Debug: All Zones":
                cv2.resizeWindow(window_name, 800, 600)
                cv2.moveWindow(window_name, 50, 50)
            elif window_name == "Debug: Current Search":
                cv2.resizeWindow(window_name, 600, 400)
                cv2.moveWindow(window_name, 870, 50)
            elif window_name == "Debug: Matches":
                cv2.resizeWindow(window_name, 600, 400)
                cv2.moveWindow(window_name, 870, 480)
            else:
                cv2.resizeWindow(window_name, 640, 480)

    def _update_window_configs(self):
        """Update stored window configurations"""
        for window_name in self.windows:
            try:
                # Get window properties (this is platform-specific and may not work on all systems)
                # For now, we'll just store that the window exists
                if window_name not in self.window_configs:
                    self.window_configs[window_name] = {}
            except:
                pass

    def reset_windows(self):
        """Reset all windows to default positions"""
        self.window_configs = {}
        for window_name in list(self.windows.keys()):
            cv2.destroyWindow(window_name)
            del self.windows[window_name]
            if window_name in self.last_images:
                # Recreate window with default settings
                self._create_window(window_name)
                cv2.imshow(window_name, self.last_images[window_name])

    def show_image(self, window_name, image, resize=True):
        """Queue an image for display"""
        if not self.running:
            return

        # Convert PIL to OpenCV if needed
        if hasattr(image, 'mode'):  # PIL Image
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        self.update_queue.put({
            'window': window_name,
            'image': image,
            'resize': resize
        })

    def show_zones(self, zones_dict, image=None):
        """Show all search zones on current screen"""
        if not self.running:
            return

        if image is None:
            screen = ImageGrab.grab()
            image = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

        # Draw all zones
        for name, region in zones_dict.items():
            color = self._get_zone_color(name)
            image = self._draw_zone(image, region, name, color)

        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(image, f"Zones @ {timestamp}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        self.show_image("Debug: All Zones", image)

    def show_search(self, template_path, region, screen=None):
        """Show current search operation"""
        if not self.running:
            return

        if screen is None:
            if region:
                screen = ImageGrab.grab(bbox=region)
            else:
                screen = ImageGrab.grab()

        image = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

        # Add search info
        info_text = f"Searching: {Path(template_path).stem}"
        cv2.putText(image, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if region:
            region_text = f"Region: {region}"
            cv2.putText(image, region_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        self.show_image("Debug: Current Search", image)

    def show_matches(self, matches, template_name, screen=None):
        """Show found matches"""
        if not self.running:
            return

        if screen is None:
            screen = ImageGrab.grab()

        image = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

        # Draw matches
        for i, (x, y, w, h) in enumerate(matches[:10]):  # Limit to 10 matches
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(image, f"{i+1}", (x+5, y+20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Add info
        info_text = f"{template_name}: {len(matches)} matches"
        cv2.putText(image, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        cv2.putText(image, timestamp, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        self.show_image("Debug: Matches", image)

    def _draw_zone(self, image, region, name, color):
        """Draw a zone rectangle with label"""
        if isinstance(region, tuple) and len(region) == 4:
            x, y, w_or_x2, h_or_y2 = region

            # Determine format
            if w_or_x2 > 200 and h_or_y2 > 200:
                x1, y1, x2, y2 = x, y, w_or_x2, h_or_y2
            else:
                x1, y1, x2, y2 = x, y, x + w_or_x2, y + h_or_y2

            # Draw rectangle
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

            # Draw label with background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            text_size = cv2.getTextSize(name, font, font_scale, thickness)[0]

            text_x = int(x1) + 2
            text_y = int(y1) - 5 if y1 > 20 else int(y2) + 15

            # Background rectangle
            cv2.rectangle(image,
                         (text_x - 2, text_y - text_size[1] - 2),
                         (text_x + text_size[0] + 2, text_y + 2),
                         (0, 0, 0), -1)

            # Text
            cv2.putText(image, name, (text_x, text_y), font, font_scale, color, thickness)

        return image

    def _get_zone_color(self, name):
        """Get color for zone by name"""
        colors = {
            "MOOD": (0, 255, 0),
            "TURN": (0, 255, 0),
            "YEAR": (0, 255, 0),
            "CRITERIA": (0, 255, 0),
            "FAILURE": (255, 0, 0),
            "SKILL_PTS": (255, 255, 0),
            "BOTTOM_SCREEN": (255, 0, 255),
            "MIDDLE_SCREEN": (255, 128, 0),
            "TOP_SCREEN": (0, 255, 255),
            "SUPPORT_CARD": (128, 0, 255),
            "ENERGY": (0, 128, 255),
            "RACE_LIST": (255, 0, 128),
        }
        return colors.get(name, (255, 255, 255))

# Global visualizer instance
_visualizer = None

def get_visualizer():
    """Get or create the global visualizer instance"""
    global _visualizer
    if _visualizer is None:
        _visualizer = DebugVisualizer()
    return _visualizer

def start_visualizer():
    """Start the real-time visualizer"""
    visualizer = get_visualizer()
    visualizer.start()

def stop_visualizer():
    """Stop the real-time visualizer"""
    global _visualizer
    if _visualizer:
        _visualizer.stop()
        _visualizer = None

def show_zones(zones_dict, image=None):
    """Show search zones in real-time window"""
    visualizer = get_visualizer()
    if visualizer.running:
        visualizer.show_zones(zones_dict, image)

def show_search(template_path, region=None, screen=None):
    """Show current search in real-time window"""
    visualizer = get_visualizer()
    if visualizer.running:
        visualizer.show_search(template_path, region, screen)

def show_matches(matches, template_name, screen=None):
    """Show matches in real-time window"""
    visualizer = get_visualizer()
    if visualizer.running:
        visualizer.show_matches(matches, template_name, screen)