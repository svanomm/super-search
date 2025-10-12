import os, json, glob, time, logging, hashlib, argparse, sys
from typing import Dict, Union, List

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

allowed_texts = ['.pdf', '.txt', '.r', '.do', '.py', '.ipynb', '.sas', '.sql', '.vba', '.md']

def file_scanner(
        filepath:str = None, 
        allowed_text_types:List[str] = allowed_texts,
        file_list_path:str = None,
        output_filename:str = None
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

    if filepath is None:
        filepath = os.getcwd()
        logging.info("You did not specify a path, so using the current working directory.")

    if file_list_path is None:
        file_list = {
            'filepath': [], 'last_modified': [], 'file_size': [], 'date_added': [], 'file_id': []
        }
    else:
        with open(file_list_path, 'r') as f:
            file_list = json.load(f)
        # Check if the file_list has the required keys
        if not all(key in file_list for key in ['filepath', 'last_modified', 'file_size', 'date_added', 'file_id']):
            raise ValueError("Invalid file list format. Missing required keys.")
        else:
            logging.info("Successfully loaded existing file list.")
            flag_existing=1
            start_length=len(file_list['filepath'])

    if output_filename is None:
        output_filename = "file_list.json"

    # Use os.walk for recursive directory traversal
    logging.info(f"Searching for files in {filepath} with allowed types: {allowed_text_types}")
    for root, dirs, files in os.walk(filepath):
        for file in files:
            # Check if the file type is allowed
            if not any(file.endswith(ext) for ext in allowed_text_types):
                continue
            
            full_path = os.path.join(root, file)
            try:
                # Get last modified time
                mod_time = os.path.getmtime(full_path)
                size = os.path.getsize(full_path)

                # Hash the file properties to uniquely identify it
                hash_id = hashlib.sha1(full_path.encode('utf-8')).hexdigest()

                # check if file-instance already in the list
                if hash_id in file_list['file_id']:
                    continue
                
                file_list['filepath'].append(full_path)
                file_list['last_modified'].append(mod_time)
                file_list['file_size'].append(int(size/(1024**2)))  # Size in MB
                file_list['date_added'].append(time.time())
                file_list['file_id'].append(hash_id)
            except (OSError, IOError) as e:
                # Skip files we can't access (permissions, etc.)
                logging.warning(f"Could not access {full_path}: {e}")
                continue
    logging.info("Done scanning.")

    if start_length > 0:
        added = len(file_list['filepath']) - start_length

    # Save to JSON file
    try:
        with open(output_filename, 'w') as f:
            json.dump(file_list, f, indent=2)
        if flag_existing == 0:
            logging.info(f"File list saved to {output_filename} with {len(file_list['filepath'])} files.")
        else:
            logging.info(f"File list updated in {output_filename} with {added} new files.")
    except IOError as e:
        logging.warning(f"Could not save to {output_filename}: {e}")

    return file_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scan directory for files and produce a JSON file list.')
    parser.add_argument('path', help='Root directory to search')
    parser.add_argument('--allowed', help='Comma-separated list of allowed extensions (e.g. .py,.md)', default=','.join(allowed_texts))
    parser.add_argument('--file-list-path', help='Path to existing file list JSON', default=None)
    parser.add_argument('--output', help='Output filename (defaults to file_list.json)', default=None)
    parser.add_argument('--verbose', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    allowed = [ext if ext.startswith('.') else '.' + ext for ext in [e.strip() for e in args.allowed.split(',') if e.strip()]]

    try:
        result = file_scanner(args.path, allowed_text_types=allowed, file_list_path=args.file_list_path, output_filename=args.output)
        logging.info(f"Scanned {len(result.get('filepath', []))} files.")
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
