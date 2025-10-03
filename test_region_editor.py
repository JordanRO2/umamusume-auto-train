#!/usr/bin/env python3
"""
Test script for the interactive region editor
Usage: python test_region_editor.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.region_editor import RegionEditor
from utils.transparent_region_editor import TransparentRegionEditor
import utils.constants as constants
from pathlib import Path
import json

def test_region_editor():
    """Test the region editor"""
    print("\n" + "="*80)
    print("REGION EDITOR TEST")
    print("="*80)
    print("\nThis will open an interactive window where you can:")
    print("1. Click and drag regions to move them")
    print("2. Drag corners to resize regions")
    print("3. Press 'n' to create new regions")
    print("4. Right-click for context menu")
    print("5. Press 'p' to print all regions to console")
    print("\nThe console will show real-time coordinates as you edit.")
    print("="*80)

    input("\nPress Enter to start the region editor...")

    editor = RegionEditor()
    editor.run()

    print("\n[TEST] Region editor test completed")

def test_transparent_editor():
    """Test the transparent overlay editor"""
    print("\n" + "="*80)
    print("TRANSPARENT OVERLAY EDITOR")
    print("="*80)
    print("\nThis will create a TRANSPARENT OVERLAY on top of your game!")
    print("\nFeatures:")
    print("  • See-through overlay - edit regions over live game")
    print("  • Drag regions directly on game screen")
    print("  • Real-time coordinate updates")
    print("  • No screenshots - works on live game")
    print("\nControls:")
    print("  • Click and drag to move/resize")
    print("  • 'n' to create new region")
    print("  • 't' to adjust transparency")
    print("  • 'h' to hide/show regions")
    print("  • ESC to exit")
    print("="*80)

    input("\nPress Enter to start transparent overlay...")

    editor = TransparentRegionEditor()
    editor.run()

    print("\n[TEST] Transparent editor test completed")

def apply_custom_regions():
    """Apply custom regions to constants"""
    custom_file = Path("debug_logs/custom_regions.json")

    if not custom_file.exists():
        print("[INFO] No custom regions file found")
        return

    print("\n" + "="*80)
    print("APPLY CUSTOM REGIONS")
    print("="*80)

    with open(custom_file, 'r') as f:
        custom = json.load(f)

    if not custom:
        print("[INFO] No custom regions defined")
        return

    print("\nCustom regions found:")
    for name, region in custom.items():
        print(f"  {name}: {region}")

    choice = input("\nApply these regions to constants? (y/n): ").strip().lower()

    if choice == 'y':
        # Here you would update constants.py
        print("\n[INFO] To apply these regions permanently:")
        print("1. Copy the following to your constants.py file:")
        print("-"*40)
        for name, region in custom.items():
            print(f"{name} = {region}")
        print("-"*40)
        print("\n2. Then use these regions in your code:")
        print("   from utils.constants import CUSTOM_REGION_NAME")
    else:
        print("[INFO] Regions not applied")

def compare_regions():
    """Compare original and custom regions"""
    custom_file = Path("debug_logs/custom_regions.json")

    print("\n" + "="*80)
    print("REGION COMPARISON")
    print("="*80)

    # Original regions
    originals = {
        "MOOD_REGION": constants.MOOD_REGION,
        "TURN_REGION": constants.TURN_REGION,
        "FAILURE_REGION": constants.FAILURE_REGION,
        "YEAR_REGION": constants.YEAR_REGION,
    }

    print("\nOriginal regions from constants.py:")
    for name, region in originals.items():
        print(f"  {name}: {region}")

    if custom_file.exists():
        with open(custom_file, 'r') as f:
            custom = json.load(f)

        if custom:
            print("\nCustom regions:")
            for name, region in custom.items():
                print(f"  {name}: {region}")

                # Check if it's a modification of an original
                if name in originals:
                    orig = originals[name]
                    if orig != region:
                        print(f"    -> Changed from: {orig}")
    else:
        print("\nNo custom regions defined yet")

def main():
    """Main test menu"""
    while True:
        print("\n" + "="*80)
        print("REGION EDITOR TEST SUITE")
        print("="*80)
        print("\n1. Open Region Editor (Screenshot-based)")
        print("2. Open TRANSPARENT Overlay Editor (Live game)")
        print("3. Apply Custom Regions to Constants")
        print("4. Compare Original vs Custom Regions")
        print("5. Show Editor Controls")
        print("0. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            test_region_editor()
        elif choice == "2":
            test_transparent_editor()
        elif choice == "3":
            apply_custom_regions()
        elif choice == "4":
            compare_regions()
        elif choice == "5":
            print("\n" + "="*80)
            print("REGION EDITOR CONTROLS")
            print("="*80)
            print("\nMOUSE CONTROLS:")
            print("  • Left Click + Drag on region center: Move region")
            print("  • Left Click + Drag on corners: Resize region")
            print("  • Right Click on region: Open context menu")
            print("    - Delete region")
            print("    - Rename region")
            print("    - Duplicate region")
            print("\nKEYBOARD CONTROLS:")
            print("  • 'n': Start creating new region (then drag)")
            print("  • 'p': Print all regions to console")
            print("  • 's': Save custom regions to file")
            print("  • 'c': Toggle coordinate display on regions")
            print("  • 'r': Refresh screen capture")
            print("  • 'h': Show help in editor")
            print("  • '1-9': Quick select regions by number")
            print("  • 'q' or ESC: Quit editor")
            print("\nTIPS:")
            print("  • Edited regions are shown in real-time in console")
            print("  • Custom regions are saved to debug_logs/custom_regions.json")
            print("  • Core regions (MOOD, TURN, etc.) cannot be deleted")
            print("  • All coordinates are in (x, y, width, height) format")
            print("\n[NOTE] Option 1 requires: pip install pywin32")
            print("       Option 2 works without any extra packages!")
            print("="*80)
        elif choice == "0":
            break
        else:
            print("[ERROR] Invalid choice")

    print("\n[EXIT] Test suite closed")

if __name__ == "__main__":
    main()