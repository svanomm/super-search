import os, json, glob, time
from typing import Dict, Union, List

allowed_texts = ['.pdf', '.txt', '.r', '.do', '.py', '.ipynb', '.sas', '.sql', '.vba', '.md']

def file_scanner(
        filepath: str, 
        allowed_text_types: List[str] = allowed_texts,
        file_list_path: str = None,
        output_filename: str = None
        ) -> Dict[str, float]:
    """
    Recursively scans a directory for files with allowed extensions, tracks their metadata, and saves the results to a JSON file.

    Args:
        filepath (str): Root directory to search for files.
        allowed_text_types (List[str], optional): List of allowed file extensions. Defaults to allowed_texts.
        file_list_path (str, optional): Path to an existing JSON file list to update. If None, starts a new list.
        output_filename (str, optional): Filename to save the resulting file list. Defaults to "file_list.json".

    Returns:
        Dict[str, float]: Dictionary containing lists of filepaths, last modified times, date added, and file IDs.
    """
    
    flag_existing=0
    start_length=0

    if file_list_path is None:
        file_list = {
            'filepath': [], 'last_modified': [], 'date_added': [], 'file_id': []
        }
    else:
        with open(file_list_path, 'r') as f:
            file_list = json.load(f)
        # Check if the file_list has the required keys
        if not all(key in file_list for key in ['filepath', 'last_modified', 'date_added', 'file_id']):
            raise ValueError("Invalid file list format. Missing required keys.")
        else:
            print("Successfully loaded existing file list.")
            flag_existing=1
            start_length=len(file_list['filepath'])

    if output_filename is None:
        output_filename = "file_list.json"

    # Use os.walk for recursive directory traversal
    print(f"Searching for files in {filepath} with allowed types: {allowed_text_types}")
    for root, dirs, files in os.walk(filepath):
        for file in files:
            # Check if the file type is allowed
            if not any(file.endswith(ext) for ext in allowed_text_types):
                continue
            
            full_path = os.path.join(root, file)
            try:
                # Get last modified time
                mod_time = os.path.getmtime(full_path)

                # We ignore the file if the same filepath and modified date are already in the list
                if full_path in file_list['filepath'] and file_list['last_modified'][file_list['filepath'].index(full_path)] == mod_time:
                    continue

                file_list['filepath'].append(full_path)
                file_list['last_modified'].append(mod_time)
                file_list['date_added'].append(time.time())
                file_list['file_id'].append(len(file_list['filepath']) - 1)  # Assign an ID based on the current length
            except (OSError, IOError) as e:
                # Skip files we can't access (permissions, etc.)
                print(f"Warning: Could not access {full_path}: {e}")
                continue
    print("Done scanning.")

    if start_length > 0:
        added = len(file_list['filepath']) - start_length

    # Save to JSON file
    try:
        with open(output_filename, 'w') as f:
            json.dump(file_list, f, indent=2)
        if flag_existing == 0:
            print(f"File list saved to {output_filename} with {len(file_list['filepath'])} files.")
        else:
            print(f"File list updated in {output_filename} with {added} new files.")
    except IOError as e:
        print(f"Warning: Could not save to {output_filename}: {e}")

    return file_list