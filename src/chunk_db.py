import os, sys, glob, pickle, lzma, time, json, logging, argparse
from tqdm import tqdm
from preprocess import prepare_PDF, prepare_text

logging.basicConfig(level=logging.INFO)

default_chunk_size = 512
default_chunk_overlap = 32

def chunk_db(
        file_list_path:str = None
        , file_list = None
        , output_file = "chunked_db"
        , chunk_size=default_chunk_size, chunk_overlap=default_chunk_overlap
        , progress_callback=None
        ):

    # If given a file_list, don't load anything
    if file_list is None:
        if file_list_path is None:
            # Search for a default location
            try:
                with open("./chunked_db.json", 'r') as f:
                    file_list = json.load(f)
            except Exception as e:
                raise ValueError("Either index_path or retriever must be provided.")
        
        # Load the file list from the given path
        with open(file_list_path, 'r') as f:
            file_list = json.load(f)

    # Check if the file_list has the required keys
    if not all(key in file_list for key in ['filepath', 'last_modified', 'file_size', 'date_added', 'file_id']):
        raise ValueError("Invalid file list format. Missing required keys.")
    else:
        logging.info("Successfully loaded existing file list.")

    full_dict = {
        'processed_chunk': []
        , 'file_id': []
    }

    assert len(file_list['filepath']) > 0, "No files found in the file list."

    # Process files
    logging.info(f"Processing {len(file_list['filepath'])} files for chunking...")
    for idx, file in enumerate(file_list['filepath']):
        logging.info(f"Processing file {idx + 1}/{len(file_list['filepath'])}: {file}")
        # Find the corresponding file_id
        f_id = file_list['file_id'][idx]

        # Confirm file exists
        if not os.path.exists(file):
            logging.warning(f"Warning: File {file} does not exist, skipping.")
            continue

        # determine file type
        if file.endswith('.pdf'):
            iter_dict = prepare_PDF(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)

        else:
            iter_dict = prepare_text(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)
        
        full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
        full_dict['file_id'].extend([f_id] * len(iter_dict['processed_chunk']))

        # Call the progress callback if provided
        if progress_callback is not None:
            progress_callback(idx + 1)

    logging.info("Done processing files.")

    # Add a chunk id field which is just the number
    logging.info("Creating chunk IDs...")
    full_dict['chunk_id'] = list(range(len(full_dict['processed_chunk'])))

    # Export as JSON
    logging.info(f"Saving chunk database to file...")
    with open(f'./{output_file}.json', 'w', encoding='utf-8') as f:
        json.dump(full_dict, f, ensure_ascii=False, indent=2)

    logging.info(f"Processed {len(full_dict['processed_chunk'])} chunks from {len(file_list['filepath'])} files.")
    logging.info(f"Data saved to ./{output_file}.json")

    return full_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create chunk database from a file list JSON.')
    parser.add_argument('--file-list-path', '-f', required=True, help='Path to file_list.json')
    parser.add_argument('--output', '-o', default='chunked_db', help='Output base filename (no extension)')
    parser.add_argument('--chunk-size', '-s', type=int, default=default_chunk_size, help='Chunk size')
    parser.add_argument('--chunk-overlap', '-c', type=int, default=default_chunk_overlap, help='Chunk overlap')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        result = chunk_db(file_list_path=args.file_list_path, output_file=args.output, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)

        # Print clickable hyperlink
        import pathlib
        output_path = os.path.abspath(f"./{args.output}.json")
        uri = pathlib.Path(output_path).as_uri()
        print(f'\x1b]8;;{uri}\x1b\\{output_path}\x1b]8;;\x1b\\')

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
