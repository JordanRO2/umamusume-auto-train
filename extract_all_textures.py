#!/usr/bin/env python3
"""
Extract ALL texture atlases from Umamusume game assets
"""

import sys
import os
from pathlib import Path
import traceback

try:
    import UnityPy
    from PIL import Image
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install: pip install UnityPy Pillow")
    sys.exit(1)

# Paths
GAME_ASSETS_PATH = Path(r"F:\New folder")  # Windows path
OUTPUT_PATH = Path("extracted_textures")

def extract_texture_file(tex_file_path, output_folder):
    """Extract textures from a single _tex file"""
    if not tex_file_path.exists():
        print(f"  ✗ File not found: {tex_file_path}")
        return 0

    output_folder.mkdir(parents=True, exist_ok=True)
    extracted_count = 0

    try:
        # Load the Unity asset
        env = UnityPy.load(str(tex_file_path))

        # Extract all textures
        for obj in env.objects:
            if obj.type.name == 'Texture2D':
                try:
                    # Read the texture data
                    data = obj.read()

                    # Get the image
                    img = data.image
                    if img:
                        # Try different ways to get the name
                        name = None

                        # Method 1: Try m_Name attribute
                        if hasattr(data, 'm_Name') and data.m_Name:
                            name = data.m_Name
                        # Method 2: Try container path
                        elif obj.container:
                            name = Path(obj.container).stem
                        # Method 3: Use object path_id
                        else:
                            name = f"texture_{obj.path_id}"

                        # Clean filename
                        name = "".join(c for c in str(name) if c.isalnum() or c in ('_', '-'))
                        if not name:
                            name = f"texture_{extracted_count}"

                        output_file = output_folder / f"{name}.png"

                        # Save the image
                        img.save(output_file)
                        print(f"    ✓ {name}.png ({img.size[0]}x{img.size[1]})")
                        extracted_count += 1

                except Exception as e:
                    print(f"    ✗ Error extracting Texture2D: {str(e)[:100]}")

            elif obj.type.name == 'Sprite':
                try:
                    # Read the sprite data
                    data = obj.read()

                    # Get the image
                    img = data.image
                    if img:
                        # Try different ways to get the name
                        name = None

                        # Method 1: Try m_Name attribute
                        if hasattr(data, 'm_Name') and data.m_Name:
                            name = data.m_Name
                        # Method 2: Use container path
                        elif obj.container:
                            name = Path(obj.container).stem
                        # Method 3: Use path_id
                        else:
                            name = f"sprite_{obj.path_id}"

                        # Clean filename
                        name = "".join(c for c in str(name) if c.isalnum() or c in ('_', '-'))
                        if not name:
                            name = f"sprite_{extracted_count}"

                        output_file = output_folder / f"{name}.png"

                        # Save the image
                        img.save(output_file)
                        print(f"    ✓ {name}.png ({img.size[0]}x{img.size[1]})")
                        extracted_count += 1

                except Exception as e:
                    print(f"    ✗ Error extracting Sprite: {str(e)[:100]}")

    except Exception as e:
        print(f"  ✗ Error loading file: {e}")

    return extracted_count

def find_all_tex_files():
    """Find all _tex files in the game assets"""
    tex_files = []

    # Search in atlas folder (priority for UI elements)
    atlas_path = GAME_ASSETS_PATH / "atlas"
    if atlas_path.exists():
        for folder in atlas_path.iterdir():
            if folder.is_dir():
                # Look for _tex files
                for file in folder.glob("*_tex*"):
                    if file.is_file():
                        tex_files.append(file)

    # Search in other folders
    other_folders = ["bg", "chara", "outgame", "uianimation", "gacha", "home",
                     "minigame", "race", "single", "story", "supportcard"]

    for folder_name in other_folders:
        folder_path = GAME_ASSETS_PATH / folder_name
        if folder_path.exists():
            # Recursively search for _tex files
            for file in folder_path.rglob("*tex*"):
                if file.is_file() and not file.suffix.endswith(('.manifest', '.mdb', '.lz4')):
                    tex_files.append(file)

    return sorted(set(tex_files))

def extract_priority_atlases():
    """Extract only the most important atlases for bot development"""
    print("="*80)
    print("EXTRACTING PRIORITY UI ATLASES FOR BOT")
    print("="*80)

    priority_files = [
        "atlas/common/common_tex",
        "atlas/home/home_tex",
        "atlas/race/race_tex",
        "atlas/single/single_tex",
        "atlas/singlecommon/singlecommon_tex",
        "atlas/option/option_tex",
        "atlas/gacha/gacha_tex",
        "atlas/racecommon/racecommon_tex",
        "atlas/shop/shop_tex",
        "atlas/mission/mission_tex",
    ]

    total_extracted = 0

    for rel_path in priority_files:
        tex_file = GAME_ASSETS_PATH / rel_path
        if tex_file.exists():
            output_folder = OUTPUT_PATH / rel_path.replace('/', os.sep)

            print(f"\nExtracting: {rel_path}")
            print(f"  File size: {tex_file.stat().st_size / 1024:.1f} KB")

            count = extract_texture_file(tex_file, output_folder)

            if count > 0:
                total_extracted += count
                print(f"  ✓ Successfully extracted {count} textures")
            else:
                print(f"  ⚠ No textures extracted")
        else:
            print(f"\n✗ Not found: {rel_path}")

    return total_extracted

def extract_all_textures():
    """Extract all texture atlases"""
    print("\n" + "="*80)
    print("EXTRACTING ALL TEXTURE ATLASES")
    print("="*80)

    # Find all texture files
    print("\nSearching for texture files...")
    tex_files = find_all_tex_files()

    if not tex_files:
        print("No texture files found!")
        return

    print(f"Found {len(tex_files)} texture files\n")

    total_extracted = 0
    successful_files = 0

    # Extract each file
    for i, tex_file in enumerate(tex_files, 1):
        # Get relative path for output folder structure
        try:
            rel_path = tex_file.relative_to(GAME_ASSETS_PATH)
        except ValueError:
            rel_path = Path(tex_file.name)

        # Create output folder maintaining structure
        output_folder = OUTPUT_PATH / rel_path.parent / rel_path.stem

        print(f"\n[{i}/{len(tex_files)}] Processing: {rel_path}")

        # Extract textures
        count = extract_texture_file(tex_file, output_folder)

        if count > 0:
            successful_files += 1
            total_extracted += count
            print(f"  ✓ Extracted {count} textures")
        else:
            print(f"  ⚠ No textures extracted")

    # Summary
    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"Files processed: {len(tex_files)}")
    print(f"Successful extractions: {successful_files}")
    print(f"Total textures extracted: {total_extracted}")
    print(f"\nOutput location: {OUTPUT_PATH.absolute()}")

def main():
    """Main function"""
    if not GAME_ASSETS_PATH.exists():
        print(f"ERROR: Game assets path not found: {GAME_ASSETS_PATH}")
        return

    # Ask what to extract
    print("="*80)
    print("UMAMUSUME TEXTURE EXTRACTOR")
    print("="*80)
    print("\n1. Extract priority UI atlases only (recommended for bot)")
    print("2. Extract ALL texture files (1000+ files)")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        extracted = extract_priority_atlases()
        print(f"\n✓ Extracted {extracted} priority textures")
        print(f"Check: {OUTPUT_PATH.absolute()}")

    elif choice == "2":
        confirm = input("\nThis will extract 1000+ files. Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            extract_all_textures()
        else:
            print("Cancelled.")

    else:
        print("Exiting.")

if __name__ == "__main__":
    main()