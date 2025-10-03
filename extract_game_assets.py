#!/usr/bin/env python3
"""
Extract UI textures from Umamusume game assets for bot template matching.
Requires: pip install UnityPy
"""

import sys
from pathlib import Path

try:
    import UnityPy
except ImportError:
    print("Please install UnityPy: pip install UnityPy")
    sys.exit(1)

# Asset paths
GAME_ASSETS_PATH = Path("/mnt/f/New folder")
OUTPUT_PATH = Path("extracted_assets")

def extract_texture_atlas(atlas_file, output_folder):
    """Extract textures from Unity atlas file"""
    if not atlas_file.exists():
        print(f"Asset file not found: {atlas_file}")
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    try:
        env = UnityPy.load(str(atlas_file))
        extracted_count = 0

        for obj in env.objects:
            if obj.type.name == 'Texture2D':
                try:
                    data = obj.read()
                    if hasattr(data, 'image') and data.image:
                        img = data.image
                        output_file = output_folder / f"{data.name}.png"
                        img.save(output_file)
                        print(f"  ✓ {data.name}.png")
                        extracted_count += 1
                except Exception as e:
                    print(f"  ✗ Error extracting texture: {e}")

        print(f"Extracted {extracted_count} textures to {output_folder}")

    except Exception as e:
        print(f"Error loading asset file {atlas_file}: {e}")

def extract_ui_assets():
    """Extract UI assets useful for bot template matching"""

    print("Extracting Umamusume UI Assets for Bot Templates")
    print("=" * 60)

    # Priority assets for bot development
    assets_to_extract = [
        ("atlas/common/common_tex", "ui/common"),           # Buttons, icons
        ("atlas/home/home_tex", "ui/home"),                 # Home screen
        ("atlas/race/race_tex", "ui/race"),                 # Race interface
        ("atlas/option/option_tex", "ui/options"),          # Settings
        ("atlas/gacha/gacha_tex", "ui/gacha"),              # Gacha interface
        ("atlas/mission/mission_tex", "ui/mission"),        # Mission UI
        ("atlas/shop/shop_tex", "ui/shop"),                 # Shop interface
        ("atlas/racecommon/racecommon_tex", "ui/race_common"), # Race common elements
    ]

    for asset_path, output_subfolder in assets_to_extract:
        full_asset_path = GAME_ASSETS_PATH / asset_path
        full_output_path = OUTPUT_PATH / output_subfolder

        print(f"\nExtracting: {asset_path}")
        extract_texture_atlas(full_asset_path, full_output_path)

    print("\n" + "=" * 60)
    print(f"Extraction complete! Check the '{OUTPUT_PATH}' folder")
    print("\nUseful extracted assets for your bot:")
    print("- ui/common/ - buttons, general UI elements")
    print("- ui/home/ - home screen elements")
    print("- ui/race/ - race interface buttons")
    print("- ui/options/ - settings menu elements")
    print("\nYou can now use these PNG files as templates in your bot!")

def create_asset_list():
    """Create a list of available assets"""
    print("\nAvailable Game Assets:")
    print("=" * 40)

    atlas_path = GAME_ASSETS_PATH / "atlas"
    if atlas_path.exists():
        for folder in sorted(atlas_path.iterdir()):
            if folder.is_dir():
                tex_file = folder / f"{folder.name}_tex"
                if tex_file.exists():
                    size_mb = tex_file.stat().st_size / (1024 * 1024)
                    print(f"  {folder.name:<15} - {size_mb:.1f}MB")

def main():
    """Main extraction function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        create_asset_list()
        return

    if not GAME_ASSETS_PATH.exists():
        print(f"Game assets path not found: {GAME_ASSETS_PATH}")
        print("Please update GAME_ASSETS_PATH in the script")
        return

    extract_ui_assets()

if __name__ == "__main__":
    main()