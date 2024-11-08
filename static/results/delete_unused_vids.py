import json
import os
import shutil
from pathlib import Path

def filter_files(root_dir, json_file, output_dir):
    """
    Create a new directory containing only the files specified in json_file,
    while preserving the directory structure.
    
    Args:
        root_dir (str): Path to the root directory
        json_file (str): Path to the JSON file containing required file paths
        output_dir (str): Path to the output directory where filtered structure will be created
    """
    # Read the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Collect all required file paths
    required_files = set()
    for scene in data:
        required_files.update(scene.get('images', []))
        required_files.update(scene.get('videos', []))
    
    # Convert paths
    root_path = Path(root_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Copy required files while preserving directory structure
    for rel_path in required_files:
        # Create source and destination paths

        if 'luma_generations' in rel_path or 'vid-only_generations' in rel_path:
            continue

        rel_path = rel_path.replace('static/results/', '')
        source_file = root_path / rel_path
        dest_file = output_path / rel_path
        
        # Create parent directories if they don't exist
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file if it exists
        if source_file.exists():
            shutil.copy2(source_file, dest_file)
            print(f"Copied: {rel_path}")
        else:
            print(f"Warning: File not found: {source_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Filter files based on JSON file paths.')
    parser.add_argument('--root_dir', help='Root directory path')
    parser.add_argument('--json_file', help='JSON file containing required file paths')
    parser.add_argument('--output_dir', help='Output directory for filtered files')
    
    args = parser.parse_args()
    filter_files(args.root_dir, args.json_file, args.output_dir)

if __name__ == "__main__":
    main()