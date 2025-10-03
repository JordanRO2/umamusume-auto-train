import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from pathlib import Path
import pygetwindow as gw
import utils.constants as constants

class SimpleTransparentEditor:
    """Simple transparent overlay region editor using only tkinter"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Region Editor - Transparent Overlay")

        # Make window transparent and always on top
        self.root.attributes('-alpha', 0.3)  # Semi-transparent
        self.root.attributes('-topmost', True)  # Always on top

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Find game window
        self.game_window = None
        self.find_game_window()

        # Position overlay
        if self.game_window:
            self.root.geometry(f"{self.game_window.width}x{self.game_window.height}+{self.game_window.left}+{self.game_window.top}")
        else:
            self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        # Make window frameless for cleaner look
        self.root.overrideredirect(True)

        # Create canvas
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='gray10')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Region management
        self.regions = {}
        self.region_rects = {}
        self.region_labels = {}
        self.selected_region = None
        self.creating_new = False
        self.new_start = None
        self.new_rect = None

        # Mouse tracking
        self.drag_data = {"x": 0, "y": 0, "item": None}

        # Load regions
        self.regions_file = Path("debug_logs/custom_regions.json")
        self.load_regions()

        # Bind events
        self.bind_events()

        # Draw regions
        self.draw_all_regions()

        # Show instructions
        self.show_instructions()

    def find_game_window(self):
        """Find the game window"""
        try:
            windows = gw.getWindowsWithTitle("Umamusume")
            if windows:
                self.game_window = windows[0]
                print(f"[INFO] Found game window: {self.game_window.title}")
                return True
        except:
            pass
        print("[INFO] Game window not found, using fullscreen")
        return False

    def load_regions(self):
        """Load regions"""
        self.regions = {
            "MOOD_REGION": constants.MOOD_REGION,
            "TURN_REGION": constants.TURN_REGION,
            "FAILURE_REGION": constants.FAILURE_REGION,
            "YEAR_REGION": constants.YEAR_REGION,
            "CRITERIA_REGION": constants.CRITERIA_REGION,
            "SKILL_PTS_REGION": constants.SKILL_PTS_REGION,
        }

        if self.regions_file.exists():
            with open(self.regions_file, 'r') as f:
                custom = json.load(f)
                self.regions.update(custom)

    def save_regions(self):
        """Save custom regions"""
        self.regions_file.parent.mkdir(exist_ok=True)

        custom = {k: v for k, v in self.regions.items()
                 if not k.endswith("_REGION") and not k.endswith("_BBOX")}

        with open(self.regions_file, 'w') as f:
            json.dump(custom, f, indent=2)

        print("[SAVED] Regions saved")
        self.print_all_regions()

    def bind_events(self):
        """Bind keyboard and mouse events"""
        # Mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # Keyboard shortcuts
        self.root.bind("<Escape>", lambda e: self.quit())
        self.root.bind("<KeyPress-n>", lambda e: self.start_new_region())
        self.root.bind("<KeyPress-s>", lambda e: self.save_regions())
        self.root.bind("<KeyPress-p>", lambda e: self.print_all_regions())
        self.root.bind("<KeyPress-t>", lambda e: self.toggle_transparency())
        self.root.bind("<KeyPress-h>", lambda e: self.show_help())
        self.root.bind("<KeyPress-q>", lambda e: self.quit())

    def convert_region(self, region):
        """Convert region format"""
        if len(region) == 4:
            x, y, w_or_x2, h_or_y2 = region
            if w_or_x2 > 500 and h_or_y2 > 500:
                return x, y, w_or_x2 - x, h_or_y2 - y
            else:
                return x, y, w_or_x2, h_or_y2
        return 0, 0, 100, 100

    def draw_all_regions(self):
        """Draw all regions"""
        # Clear existing
        for item in self.region_rects.values():
            self.canvas.delete(item)
        for item in self.region_labels.values():
            self.canvas.delete(item)

        self.region_rects.clear()
        self.region_labels.clear()

        # Draw each region
        for name, region in self.regions.items():
            self.draw_region(name, region)

    def draw_region(self, name, region):
        """Draw a single region"""
        x, y, w, h = self.convert_region(region)

        # Choose color
        if "MOOD" in name or "TURN" in name:
            color = "#00FF00"
        elif "FAILURE" in name:
            color = "#FF0000"
        elif "SKILL" in name:
            color = "#FFFF00"
        else:
            color = "#00FFFF"

        # Draw rectangle
        rect = self.canvas.create_rectangle(
            x, y, x + w, y + h,
            outline=color,
            width=2,
            tags=(name, "region")
        )

        # Draw label
        label_text = f"{name}\n{x},{y},{w},{h}"
        label = self.canvas.create_text(
            x + 5, y + 5,
            text=label_text,
            anchor="nw",
            fill=color,
            font=("Arial", 8),
            tags=(f"{name}_label", "label")
        )

        self.region_rects[name] = rect
        self.region_labels[name] = label

    def on_click(self, event):
        """Handle click"""
        if self.creating_new:
            self.new_start = (event.x, event.y)
            self.new_rect = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline="#FF00FF", width=2, dash=(5, 5)
            )
        else:
            # Find clicked region
            item = self.canvas.find_closest(event.x, event.y)[0]
            tags = self.canvas.gettags(item)

            if "region" in tags:
                self.selected_region = tags[0]
                self.drag_data = {"x": event.x, "y": event.y, "item": item}

                # Highlight selected
                self.canvas.itemconfig(item, width=3)

    def on_drag(self, event):
        """Handle drag"""
        if self.creating_new and self.new_rect:
            # Update new region
            x1, y1 = self.new_start
            self.canvas.coords(self.new_rect, x1, y1, event.x, event.y)

            # Show size
            w = abs(event.x - x1)
            h = abs(event.y - y1)
            print(f"\rNew: ({min(x1,event.x)}, {min(y1,event.y)}, {w}, {h})    ", end="")

        elif self.drag_data["item"] and self.selected_region:
            # Move region
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]

            rect = self.region_rects[self.selected_region]
            label = self.region_labels[self.selected_region]

            self.canvas.move(rect, dx, dy)
            self.canvas.move(label, dx, dy)

            # Update position
            x1, y1, x2, y2 = self.canvas.coords(rect)
            w = int(x2 - x1)
            h = int(y2 - y1)

            self.regions[self.selected_region] = (int(x1), int(y1), w, h)

            # Update label
            self.canvas.itemconfig(label, text=f"{self.selected_region}\n{int(x1)},{int(y1)},{w},{h}")

            print(f"\r{self.selected_region} = ({int(x1)}, {int(y1)}, {w}, {h})    ", end="")

            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_release(self, event):
        """Handle release"""
        if self.creating_new and self.new_rect:
            x1, y1 = self.new_start
            x2, y2 = event.x, event.y

            rx = min(x1, x2)
            ry = min(y1, y2)
            rw = abs(x2 - x1)
            rh = abs(y2 - y1)

            if rw > 10 and rh > 10:
                # Simple input dialog
                name = simpledialog.askstring("New Region", "Enter name:")
                if name:
                    self.regions[name] = (rx, ry, rw, rh)
                    self.draw_region(name, (rx, ry, rw, rh))
                    print(f"\n[NEW] {name} = ({rx}, {ry}, {rw}, {rh})")

            self.canvas.delete(self.new_rect)
            self.new_rect = None
            self.new_start = None
            self.creating_new = False

        self.drag_data = {"x": 0, "y": 0, "item": None}

    def on_right_click(self, event):
        """Handle right click"""
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)

        if "region" in tags:
            region_name = tags[0]

            # Simple menu
            if messagebox.askyesno("Delete", f"Delete {region_name}?"):
                if region_name in self.region_rects:
                    self.canvas.delete(self.region_rects[region_name])
                    self.canvas.delete(self.region_labels[region_name])
                    del self.regions[region_name]
                    print(f"[DELETED] {region_name}")

    def start_new_region(self):
        """Start creating new region"""
        self.creating_new = True
        print("\n[NEW] Click and drag to create...")

    def toggle_transparency(self):
        """Toggle transparency"""
        alpha = self.root.attributes('-alpha')
        if alpha < 0.3:
            self.root.attributes('-alpha', 0.3)
            print("[ALPHA] 30%")
        elif alpha < 0.5:
            self.root.attributes('-alpha', 0.5)
            print("[ALPHA] 50%")
        elif alpha < 0.7:
            self.root.attributes('-alpha', 0.7)
            print("[ALPHA] 70%")
        else:
            self.root.attributes('-alpha', 0.1)
            print("[ALPHA] 10%")

    def print_all_regions(self):
        """Print all regions"""
        print("\n" + "="*60)
        print("REGIONS (Copy to constants.py):")
        print("="*60)
        for name, region in sorted(self.regions.items()):
            x, y, w, h = self.convert_region(region)
            print(f"{name} = ({x}, {y}, {w}, {h})")
        print("="*60 + "\n")

    def show_help(self):
        """Show help"""
        print("\nCONTROLS:")
        print("  n - New region")
        print("  s - Save")
        print("  p - Print all")
        print("  t - Toggle transparency")
        print("  q/ESC - Quit")
        print("  Left click - Select/drag")
        print("  Right click - Delete")

    def show_instructions(self):
        """Show initial instructions"""
        print("\n" + "="*60)
        print("TRANSPARENT REGION EDITOR")
        print("="*60)
        print("\nOverlay is now on your screen!")
        print("\nKEYBOARD:")
        print("  n - New region")
        print("  s - Save")
        print("  p - Print all")
        print("  t - Transparency")
        print("  h - Help")
        print("  ESC - Exit")
        print("\nMOUSE:")
        print("  Drag - Move regions")
        print("  Right click - Delete")
        print("="*60 + "\n")

    def quit(self):
        """Exit"""
        self.save_regions()
        self.print_all_regions()
        print("[EXIT] Closed")
        self.root.destroy()

    def run(self):
        """Run the editor"""
        self.root.mainloop()

def main():
    editor = SimpleTransparentEditor()
    editor.run()

if __name__ == "__main__":
    main()