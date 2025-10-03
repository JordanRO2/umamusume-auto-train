import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from pathlib import Path
import win32gui
import win32con
import win32api
import pygetwindow as gw
import utils.constants as constants
import threading
import time

class TransparentRegionEditor:
    """Transparent overlay region editor that sits on top of the game window"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Region Editor - Transparent Overlay")

        # Make window transparent and always on top
        self.root.attributes('-alpha', 0.3)  # Semi-transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-fullscreen', False)

        # Remove window decorations for cleaner overlay
        self.root.overrideredirect(True)

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Find game window
        self.game_window = None
        self.find_game_window()

        # Position overlay over game window or fullscreen
        if self.game_window:
            self.root.geometry(f"{self.game_window.width}x{self.game_window.height}+{self.game_window.left}+{self.game_window.top}")
        else:
            self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        # Create transparent canvas
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Make canvas transparent with colored regions
        self.canvas.configure(bg='black')

        # Region management
        self.regions = {}
        self.region_rects = {}  # Canvas rectangle objects
        self.region_labels = {}  # Canvas text objects
        self.selected_region = None
        self.drag_data = {"x": 0, "y": 0, "item": None, "action": None}

        # Load regions
        self.regions_file = Path("debug_logs/custom_regions.json")
        self.load_regions()

        # Control panel (small, draggable)
        self.create_control_panel()

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right click
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

        # Bind keyboard events
        self.root.bind("<Escape>", lambda e: self.quit())
        self.root.bind("<KeyPress-n>", lambda e: self.start_new_region())
        self.root.bind("<KeyPress-s>", lambda e: self.save_regions())
        self.root.bind("<KeyPress-p>", lambda e: self.print_all_regions())
        self.root.bind("<KeyPress-h>", lambda e: self.toggle_visibility())
        self.root.bind("<KeyPress-t>", lambda e: self.toggle_transparency())
        self.root.bind("<Delete>", lambda e: self.delete_selected())

        # New region creation
        self.creating_new = False
        self.new_region_start = None
        self.new_region_rect = None

        # Draw initial regions
        self.draw_all_regions()

        # Auto-save timer
        self.auto_save_timer()

        print("\n" + "="*80)
        print("TRANSPARENT REGION EDITOR")
        print("="*80)
        print("\nThe editor is now overlaid on your game window!")
        print("\nKEYBOARD SHORTCUTS:")
        print("  'n' - Create new region")
        print("  's' - Save regions")
        print("  'p' - Print all regions to console")
        print("  'h' - Hide/show regions")
        print("  't' - Toggle transparency level")
        print("  'Delete' - Delete selected region")
        print("  'Escape' - Exit editor")
        print("\nMOUSE CONTROLS:")
        print("  Left Click - Select region")
        print("  Drag - Move region or resize from edges")
        print("  Right Click - Context menu")
        print("  Double Click - Edit region name")
        print("="*80 + "\n")

    def find_game_window(self):
        """Find the game window"""
        try:
            # Try to find Umamusume window
            windows = gw.getWindowsWithTitle("Umamusume")
            if windows:
                self.game_window = windows[0]
                print(f"[INFO] Found game window: {self.game_window.title}")
                return True

            # Try alternative window name
            import core.state as state
            if hasattr(state, 'WINDOW_NAME') and state.WINDOW_NAME:
                windows = gw.getWindowsWithTitle(state.WINDOW_NAME)
                if windows:
                    self.game_window = windows[0]
                    print(f"[INFO] Found game window: {self.game_window.title}")
                    return True
        except:
            pass

        print("[INFO] Game window not found, using fullscreen overlay")
        return False

    def load_regions(self):
        """Load regions from constants and custom file"""
        # Load from constants
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

        # Load custom regions
        if self.regions_file.exists():
            with open(self.regions_file, 'r') as f:
                custom = json.load(f)
                self.regions.update(custom)

    def save_regions(self):
        """Save custom regions to file"""
        self.regions_file.parent.mkdir(exist_ok=True)

        # Filter custom regions
        custom_regions = {k: v for k, v in self.regions.items()
                         if not k.endswith("_REGION") and not k.endswith("_BBOX")}

        with open(self.regions_file, 'w') as f:
            json.dump(custom_regions, f, indent=2)

        print("[SAVED] Regions saved to debug_logs/custom_regions.json")
        self.print_all_regions()

    def convert_region(self, region):
        """Convert region to (x, y, width, height) format"""
        if len(region) == 4:
            x, y, w_or_x2, h_or_y2 = region
            if w_or_x2 > 500 and h_or_y2 > 500:  # Likely x2, y2
                return x, y, w_or_x2 - x, h_or_y2 - y
            else:
                return x, y, w_or_x2, h_or_y2
        return 0, 0, 100, 100

    def draw_all_regions(self):
        """Draw all regions on the canvas"""
        # Clear existing
        for rect in self.region_rects.values():
            self.canvas.delete(rect)
        for label in self.region_labels.values():
            self.canvas.delete(label)

        self.region_rects.clear()
        self.region_labels.clear()

        # Draw regions
        for name, region in self.regions.items():
            self.draw_region(name, region)

    def draw_region(self, name, region):
        """Draw a single region"""
        x, y, w, h = self.convert_region(region)

        # Choose color based on type
        if "MOOD" in name or "TURN" in name or "YEAR" in name:
            color = "#00FF00"  # Green
        elif "FAILURE" in name:
            color = "#FF0000"  # Red
        elif "SKILL" in name:
            color = "#FFFF00"  # Yellow
        elif "SCREEN" in name:
            color = "#FF00FF"  # Magenta
        else:
            color = "#00FFFF"  # Cyan

        # Draw rectangle
        rect = self.canvas.create_rectangle(
            x, y, x + w, y + h,
            outline=color,
            width=2,
            fill="",  # No fill for transparency
            tags=(name, "region")
        )

        # Draw label
        label = self.canvas.create_text(
            x + 5, y + 5,
            text=f"{name}\n({x},{y},{w},{h})",
            anchor="nw",
            fill=color,
            font=("Arial", 9),
            tags=(name + "_label", "label")
        )

        self.region_rects[name] = rect
        self.region_labels[name] = label

    def on_click(self, event):
        """Handle mouse click"""
        if self.creating_new:
            # Start creating new region
            self.new_region_start = (event.x, event.y)
            self.new_region_rect = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline="#FF00FF",
                width=2,
                dash=(5, 5)
            )
        else:
            # Find clicked item
            item = self.canvas.find_closest(event.x, event.y)[0]
            tags = self.canvas.gettags(item)

            if "region" in tags:
                # Select region
                region_name = tags[0]
                self.select_region(region_name)

                # Check if clicking on edge for resize
                x1, y1, x2, y2 = self.canvas.coords(item)
                edge_threshold = 10

                if abs(event.x - x1) < edge_threshold:
                    self.drag_data["action"] = "resize_left"
                elif abs(event.x - x2) < edge_threshold:
                    self.drag_data["action"] = "resize_right"
                elif abs(event.y - y1) < edge_threshold:
                    self.drag_data["action"] = "resize_top"
                elif abs(event.y - y2) < edge_threshold:
                    self.drag_data["action"] = "resize_bottom"
                else:
                    self.drag_data["action"] = "move"

                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                self.drag_data["item"] = item

    def on_drag(self, event):
        """Handle mouse drag"""
        if self.creating_new and self.new_region_rect:
            # Update new region preview
            x1, y1 = self.new_region_start
            self.canvas.coords(self.new_region_rect, x1, y1, event.x, event.y)

            # Show size in console
            w = abs(event.x - x1)
            h = abs(event.y - y1)
            print(f"\rNew region: ({min(x1, event.x)}, {min(y1, event.y)}, {w}, {h})    ", end="", flush=True)

        elif self.drag_data["item"] and self.selected_region:
            # Move or resize existing region
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]

            rect = self.region_rects[self.selected_region]
            label = self.region_labels[self.selected_region]
            x1, y1, x2, y2 = self.canvas.coords(rect)

            if self.drag_data["action"] == "move":
                # Move region
                self.canvas.move(rect, dx, dy)
                self.canvas.move(label, dx, dy)
            elif self.drag_data["action"] == "resize_left":
                self.canvas.coords(rect, x1 + dx, y1, x2, y2)
            elif self.drag_data["action"] == "resize_right":
                self.canvas.coords(rect, x1, y1, x2 + dx, y2)
            elif self.drag_data["action"] == "resize_top":
                self.canvas.coords(rect, x1, y1 + dy, x2, y2)
            elif self.drag_data["action"] == "resize_bottom":
                self.canvas.coords(rect, x1, y1, x2, y2 + dy)

            # Update label position and text
            x1, y1, x2, y2 = self.canvas.coords(rect)
            w = int(x2 - x1)
            h = int(y2 - y1)
            self.canvas.coords(label, x1 + 5, y1 + 5)
            self.canvas.itemconfig(label, text=f"{self.selected_region}\n({int(x1)},{int(y1)},{w},{h})")

            # Update stored region
            self.regions[self.selected_region] = (int(x1), int(y1), w, h)

            # Print to console
            print(f"\r[REGION] {self.selected_region} = ({int(x1)}, {int(y1)}, {w}, {h})    ", end="", flush=True)

            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_release(self, event):
        """Handle mouse release"""
        if self.creating_new and self.new_region_rect:
            # Finish creating new region
            x1, y1 = self.new_region_start
            x2, y2 = event.x, event.y

            # Normalize coordinates
            rx = min(x1, x2)
            ry = min(y1, y2)
            rw = abs(x2 - x1)
            rh = abs(y2 - y1)

            if rw > 10 and rh > 10:
                # Ask for region name
                name = simpledialog.askstring("New Region", "Enter name for new region:")
                if name:
                    self.regions[name] = (rx, ry, rw, rh)
                    self.draw_region(name, (rx, ry, rw, rh))
                    print(f"\n[CREATED] {name} = ({rx}, {ry}, {rw}, {rh})")
                    self.save_regions()

            # Clean up
            self.canvas.delete(self.new_region_rect)
            self.new_region_rect = None
            self.new_region_start = None
            self.creating_new = False

        # Reset drag data
        self.drag_data = {"x": 0, "y": 0, "item": None, "action": None}

    def on_right_click(self, event):
        """Handle right click for context menu"""
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)

        if "region" in tags:
            region_name = tags[0]

            # Create context menu
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label=f"Edit {region_name}", command=lambda: self.edit_region(region_name))
            menu.add_command(label=f"Delete {region_name}", command=lambda: self.delete_region(region_name))
            menu.add_command(label=f"Duplicate {region_name}", command=lambda: self.duplicate_region(region_name))
            menu.add_separator()
            menu.add_command(label="Print to Console", command=lambda: self.print_region(region_name))

            menu.post(event.x_root, event.y_root)

    def on_double_click(self, event):
        """Handle double click to edit region name"""
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)

        if "region" in tags:
            region_name = tags[0]
            self.edit_region(region_name)

    def select_region(self, name):
        """Select a region"""
        # Reset all region colors
        for region_name, rect in self.region_rects.items():
            if region_name == name:
                self.canvas.itemconfig(rect, width=3, dash=())
                self.selected_region = name
            else:
                self.canvas.itemconfig(rect, width=2, dash=())

    def delete_region(self, name):
        """Delete a region"""
        if name in ["MOOD_REGION", "TURN_REGION", "YEAR_REGION"]:
            messagebox.showerror("Error", f"Cannot delete core region '{name}'")
            return

        if messagebox.askyesno("Delete Region", f"Delete region '{name}'?"):
            # Remove from canvas
            if name in self.region_rects:
                self.canvas.delete(self.region_rects[name])
                del self.region_rects[name]
            if name in self.region_labels:
                self.canvas.delete(self.region_labels[name])
                del self.region_labels[name]

            # Remove from regions
            if name in self.regions:
                del self.regions[name]
                print(f"[DELETED] Region '{name}'")
                self.save_regions()

    def delete_selected(self):
        """Delete currently selected region"""
        if self.selected_region:
            self.delete_region(self.selected_region)
            self.selected_region = None

    def edit_region(self, name):
        """Edit region name"""
        new_name = simpledialog.askstring("Edit Region", f"Enter new name for '{name}':", initialvalue=name)
        if new_name and new_name != name:
            if new_name in self.regions:
                messagebox.showerror("Error", f"Region '{new_name}' already exists")
                return

            # Update region
            self.regions[new_name] = self.regions.pop(name)

            # Redraw
            self.draw_all_regions()
            print(f"[RENAMED] '{name}' -> '{new_name}'")
            self.save_regions()

    def duplicate_region(self, name):
        """Duplicate a region"""
        new_name = simpledialog.askstring("Duplicate Region", f"Enter name for copy of '{name}':")
        if new_name:
            if new_name in self.regions:
                messagebox.showerror("Error", f"Region '{new_name}' already exists")
                return

            # Copy region with slight offset
            x, y, w, h = self.convert_region(self.regions[name])
            self.regions[new_name] = (x + 20, y + 20, w, h)
            self.draw_region(new_name, self.regions[new_name])
            print(f"[COPIED] '{name}' -> '{new_name}'")
            self.save_regions()

    def print_region(self, name):
        """Print single region to console"""
        if name in self.regions:
            x, y, w, h = self.convert_region(self.regions[name])
            print(f"\n{name} = ({x}, {y}, {w}, {h})")

    def print_all_regions(self):
        """Print all regions to console"""
        print("\n" + "="*80)
        print("CURRENT REGIONS (Copy to constants.py):")
        print("="*80)

        for name, region in sorted(self.regions.items()):
            x, y, w, h = self.convert_region(region)
            print(f"{name} = ({x}, {y}, {w}, {h})")

        print("="*80 + "\n")

    def start_new_region(self):
        """Start creating a new region"""
        self.creating_new = True
        print("\n[NEW] Click and drag to create new region...")

    def toggle_visibility(self):
        """Toggle region visibility"""
        if self.canvas.winfo_viewable():
            self.canvas.pack_forget()
            print("[HIDDEN] Regions hidden (press 'h' to show)")
        else:
            self.canvas.pack(fill=tk.BOTH, expand=True)
            print("[VISIBLE] Regions visible")

    def toggle_transparency(self):
        """Toggle transparency level"""
        current_alpha = self.root.attributes('-alpha')
        if current_alpha < 0.3:
            self.root.attributes('-alpha', 0.3)
            print("[TRANSPARENCY] 30%")
        elif current_alpha < 0.5:
            self.root.attributes('-alpha', 0.5)
            print("[TRANSPARENCY] 50%")
        elif current_alpha < 0.7:
            self.root.attributes('-alpha', 0.7)
            print("[TRANSPARENCY] 70%")
        else:
            self.root.attributes('-alpha', 0.1)
            print("[TRANSPARENCY] 10%")

    def create_control_panel(self):
        """Create a small control panel"""
        # Create a small draggable control window
        control = tk.Toplevel(self.root)
        control.title("Controls")
        control.geometry("200x150+10+10")
        control.attributes('-topmost', True)
        control.attributes('-alpha', 0.9)

        # Make it draggable
        control.overrideredirect(False)

        # Add buttons
        ttk.Button(control, text="New Region (N)", command=self.start_new_region).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(control, text="Save (S)", command=self.save_regions).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(control, text="Print All (P)", command=self.print_all_regions).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(control, text="Toggle Transparency (T)", command=self.toggle_transparency).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(control, text="Exit (ESC)", command=self.quit).pack(fill=tk.X, padx=5, pady=2)

        self.control_panel = control

    def auto_save_timer(self):
        """Auto-save regions periodically"""
        self.save_regions()
        self.root.after(30000, self.auto_save_timer)  # Auto-save every 30 seconds

    def quit(self):
        """Exit the editor"""
        self.save_regions()
        self.print_all_regions()
        print("[EXIT] Region editor closed")
        self.root.quit()

    def run(self):
        """Run the editor"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit()

def main():
    """Run the transparent region editor"""
    editor = TransparentRegionEditor()
    editor.run()

if __name__ == "__main__":
    main()