import os
import json
import time
from typing import Dict, Union, List


def create_new_list(filepath: str, output_filename: str = None) -> Dict[str, float]:
    """
    Scans the given directory recursively and collects all files with their last modified dates.
    
    Args:
        filepath (str): Path to the directory to scan recursively.
        output_filename (str, optional): Output JSON filename. If None, uses 'file_list.json'.
    
    Returns:
        dict: Dictionary mapping file paths to their last modified timestamps.
    """
    if not os.path.exists(filepath):
        raise ValueError(f"Path does not exist: {filepath}")
    
    if not os.path.isdir(filepath):
        raise ValueError(f"Path is not a directory: {filepath}")
    
    file_list = {}
    
    # Use os.walk for recursive directory traversal
    for root, dirs, files in os.walk(filepath):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                # Get last modified time
                mod_time = os.path.getmtime(full_path)
                file_list[full_path] = mod_time
            except (OSError, IOError) as e:
                # Skip files we can't access (permissions, etc.)
                print(f"Warning: Could not access {full_path}: {e}")
                continue
    
    # Save to JSON file
    if output_filename is None:
        output_filename = "file_list.json"
    
    try:
        with open(output_filename, 'w') as f:
            json.dump(file_list, f, indent=2)
        print(f"File list saved to {output_filename}")
    except IOError as e:
        print(f"Warning: Could not save to {output_filename}: {e}")
    
    return file_list


def update_list(filepath: str, existing_file_list: Union[str, Dict[str, float]], 
                output_filename: str = None) -> Dict[str, float]:
    """
    Scans the given directory recursively and updates an existing file list with new or modified files.
    
    Args:
        filepath (str): Path to the directory to scan recursively.
        existing_file_list (Union[str, Dict[str, float]]): Either a path to existing JSON file 
                                                          or a dictionary of existing files.
        output_filename (str, optional): Output JSON filename. If None, overwrites existing file
                                        if existing_file_list is a file path, otherwise uses 'updated_file_list.json'.
    
    Returns:
        dict: Updated dictionary mapping file paths to their last modified timestamps.
    """
    if not os.path.exists(filepath):
        raise ValueError(f"Path does not exist: {filepath}")
    
    if not os.path.isdir(filepath):
        raise ValueError(f"Path is not a directory: {filepath}")
    
    # Load existing file list
    if isinstance(existing_file_list, str):
        # It's a file path
        if not os.path.exists(existing_file_list):
            raise ValueError(f"Existing file list does not exist: {existing_file_list}")
        
        try:
            with open(existing_file_list, 'r') as f:
                existing_files = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise ValueError(f"Could not load existing file list: {e}")
        
        # Set default output filename to overwrite the existing file
        if output_filename is None:
            output_filename = existing_file_list
    else:
        # It's already a dictionary
        existing_files = existing_file_list.copy()
        if output_filename is None:
            output_filename = "updated_file_list.json"
    
    # Start with existing files
    updated_list = existing_files.copy()
    
    # Scan directory for current files
    current_files = {}
    for root, dirs, files in os.walk(filepath):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                mod_time = os.path.getmtime(full_path)
                current_files[full_path] = mod_time
            except (OSError, IOError) as e:
                print(f"Warning: Could not access {full_path}: {e}")
                continue
    
    # Update list with new or modified files
    new_files_count = 0
    modified_files_count = 0
    
    for file_path, mod_time in current_files.items():
        if file_path not in existing_files:
            # New file
            updated_list[file_path] = mod_time
            new_files_count += 1
        elif existing_files[file_path] != mod_time:
            # Modified file (different timestamp)
            updated_list[file_path] = mod_time
            modified_files_count += 1
    
    print(f"Found {new_files_count} new files and {modified_files_count} modified files")
    
    # Save updated list
    try:
        with open(output_filename, 'w') as f:
            json.dump(updated_list, f, indent=2)
        print(f"Updated file list saved to {output_filename}")
    except IOError as e:
        print(f"Warning: Could not save to {output_filename}: {e}")
    
    return updated_list


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python file_scanner.py <directory_path> [create|update] [existing_file_list]")
        print("Examples:")
        print("  python file_scanner.py /path/to/scan create")
        print("  python file_scanner.py /path/to/scan update existing_list.json")
        sys.exit(1)
    
    directory = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "create"
    
    if action == "create":
        result = create_new_list(directory)
        print(f"Created file list with {len(result)} files")
    elif action == "update":
        if len(sys.argv) < 4:
            print("Error: update action requires existing file list path")
            sys.exit(1)
        existing_list = sys.argv[3]
        result = update_list(directory, existing_list)
        print(f"Updated file list now contains {len(result)} files")
    else:
        print(f"Unknown action: {action}. Use 'create' or 'update'")
        sys.exit(1)