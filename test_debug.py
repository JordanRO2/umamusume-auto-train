#!/usr/bin/env python3
"""
Test script for debug mode functionality
Usage: python test_debug.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.debug_mode import (
    enable_debug_mode, disable_debug_mode, visualize_all_zones,
    log_message, save_debug_screenshot, cleanup_old_logs
)
from utils.log import info, debug
import utils.constants as constants
from core.recognizer import match_template, multi_match_templates
from PIL import ImageGrab
import cv2
import time
from pathlib import Path

def test_logging():
    """Test logging functionality"""
    print("\n=== Testing Logging System ===")
    enable_debug_mode(show_zones=False, step_mode=False)

    log_message("Test log message 1")
    log_message("Test warning message", "WARNING")
    log_message("Test error message", "ERROR")

    # Test search logging
    from utils.debug_mode import log_search_attempt
    log_search_attempt("test_search_1", region=(0, 0, 100, 100), success=True, details="Found 3 matches")
    log_search_attempt("test_search_2", region=(100, 100, 200, 200), success=False, details="No matches")

    disable_debug_mode()

    # Check if logs were created
    log_dir = Path("debug_logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"Created {len(log_files)} log files")
        for log_file in log_files:
            print(f"  - {log_file.name} ({log_file.stat().st_size} bytes)")
    else:
        print("No log directory created")

    print("Logging test complete")

def test_zone_saving():
    """Test zone visualization saving to file"""
    print("\n=== Testing Zone Saving ===")
    enable_debug_mode(show_zones=True, step_mode=False)

    # Visualize and save zones
    print("Capturing and saving zone visualization...")
    image = visualize_all_zones(save_to_file=True, show_window=False)

    if image is not None:
        print("Zone visualization saved to debug_logs/")

        # Check if file was created
        log_dir = Path("debug_logs")
        zone_files = list(log_dir.glob("all_zones_*.png"))
        if zone_files:
            print(f"Found {len(zone_files)} zone visualization files")
            for zone_file in zone_files:
                print(f"  - {zone_file.name} ({zone_file.stat().st_size} bytes)")
    else:
        print("Failed to visualize zones")

    disable_debug_mode()
    print("Zone saving test complete")

def test_search_logging():
    """Test template matching with logging"""
    print("\n=== Testing Search Logging ===")
    enable_debug_mode(show_zones=True, step_mode=False)

    # Test single template match
    print("Testing single template match with logging...")
    matches = match_template("assets/buttons/next_btn.png", threshold=0.8)
    print(f"Found {len(matches)} matches")

    # Test multi-template match
    templates = {
        "next": "assets/buttons/next_btn.png",
        "cancel": "assets/buttons/cancel_btn.png",
        "back": "assets/buttons/back_btn.png",
    }
    print("Testing multi-template match with logging...")
    results = multi_match_templates(templates, threshold=0.8)
    for name, boxes in results.items():
        print(f"  {name}: {len(boxes)} matches")

    disable_debug_mode()

    # Show log contents
    log_dir = Path("debug_logs")
    search_log = log_dir / "search_history.log"
    if search_log.exists():
        print("\nSearch history log contents:")
        with open(search_log, 'r') as f:
            lines = f.readlines()[-10:]  # Last 10 lines
            for line in lines:
                print(f"  {line.rstrip()}")

    print("Search logging test complete")

def test_step_mode_non_blocking():
    """Test step-by-step mode without blocking displays"""
    print("\n=== Testing Non-Blocking Step Mode ===")
    enable_debug_mode(show_zones=True, step_mode=True)

    print("Step mode enabled. Press Enter after each step.")
    print("All visualizations will be saved to files instead of blocking windows.")

    # Test a simple search
    print("\nSearching for next button...")
    matches = match_template("assets/buttons/next_btn.png", threshold=0.8)
    print(f"Search complete. Found {len(matches)} matches")

    disable_debug_mode()
    print("Non-blocking step mode test complete")

def view_logs():
    """View recent log files"""
    log_dir = Path("debug_logs")
    if not log_dir.exists():
        print("No debug_logs directory found")
        return

    print("\n=== Log Files ===")
    log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not log_files:
        print("No log files found")
        return

    for i, log_file in enumerate(log_files[:5]):
        size = log_file.stat().st_size
        mtime = time.ctime(log_file.stat().st_mtime)
        print(f"{i+1}. {log_file.name} - {size:,} bytes - {mtime}")

    choice = input("\nEnter number to view log (or press Enter to skip): ").strip()
    if choice and choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(log_files):
            print(f"\n=== Contents of {log_files[idx].name} ===")
            with open(log_files[idx], 'r') as f:
                lines = f.readlines()
                if len(lines) > 50:
                    print(f"(Showing last 50 lines of {len(lines)} total)\n")
                    lines = lines[-50:]
                for line in lines:
                    print(line.rstrip())

def cleanup_logs():
    """Clean up old log files"""
    print("\n=== Cleaning Up Logs ===")
    cleanup_old_logs(keep_last_n=5)
    print("Cleanup complete (keeping last 5 debug logs)")

def main():
    print("Debug Mode Test Suite - Non-Blocking Version")
    print("=" * 50)
    print("All visualizations will be saved to debug_logs/")
    print("No blocking windows will be shown\n")

    while True:
        print("\nSelect a test:")
        print("1. Test logging system")
        print("2. Test zone visualization (save to file)")
        print("3. Test search with logging")
        print("4. Test non-blocking step mode")
        print("5. View log files")
        print("6. Clean up old logs")
        print("7. Run all tests")
        print("0. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            test_logging()
        elif choice == "2":
            test_zone_saving()
        elif choice == "3":
            test_search_logging()
        elif choice == "4":
            test_step_mode_non_blocking()
        elif choice == "5":
            view_logs()
        elif choice == "6":
            cleanup_logs()
        elif choice == "7":
            test_logging()
            test_zone_saving()
            test_search_logging()
            print("\n[Note: Skipping step mode in batch test]")
        elif choice == "0":
            break
        else:
            print("Invalid choice")

    print("\nAll tests complete!")
    print(f"Check the debug_logs/ directory for saved files")

if __name__ == "__main__":
    main()