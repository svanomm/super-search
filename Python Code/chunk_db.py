import os, sys, glob, pickle, lzma, time, json
from tqdm import tqdm
from preprocess import prepare_PDF, prepare_text

def chunk_db(
        file_list_path:str = None
        , file_list = None
        , output_file = "chunked_db"
        , chunk_size=2056, chunk_overlap=16
        ):

    # If given a file_list, don't load anything
    if file_list is None:
        if file_list_path is None:
            raise ValueError("Either file_list or file_list_path must be provided.")
        
        # Load the file list from the given path
        print(f"Loading file list from {file_list_path}")
        with open(file_list_path, 'r') as f:
            file_list = json.load(f)

    # Check if the file_list has the required keys
    if not all(key in file_list for key in ['filepath', 'last_modified', 'date_added', 'file_id']):
        raise ValueError("Invalid file list format. Missing required keys.")
    else:
        print("Successfully loaded existing file list.")

    full_dict = {
        'processed_chunk': []
        , 'file_id': []
    }

    assert len(file_list['filepath']) > 0, "No files found in the file list."

    # Process files
    print(f"Processing {len(file_list['filepath'])} files for chunking...")
    for file in tqdm(file_list['filepath'], desc = "Chunking Files"):
        # Find the corresponding file_id
        row = file_list['filepath'].index(file)
        f_id = file_list['file_id'][row]

        # Confirm file exists
        if not os.path.exists(file):
            print(f"Warning: File {file} does not exist, skipping.")
            continue

        # determine file type
        if file.endswith('.pdf'):
            iter_dict = prepare_PDF(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)

        else:
            iter_dict = prepare_text(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)
        
        full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
        full_dict['file_id'].extend([f_id] * len(iter_dict['processed_chunk']))

    print("Done processing files.")

    # Add a chunk id field which is just the number
    print("Finalizing chunk database...")
    full_dict['chunk_id'] = list(range(len(full_dict['processed_chunk'])))

    # Export as JSON
    print(f"Saving chunk database to file...")
    with tqdm(total=1, desc="Writing JSON file", unit="file") as pbar:
        with open(f'../{output_file}.json', 'w', encoding='utf-8') as f:
            json.dump(full_dict, f, ensure_ascii=False, indent=2)
        pbar.update(1)

    print(f"Processed {len(full_dict['processed_chunk'])} chunks from {len(file_list['filepath'])} files.")
    print(f"Data saved to ../{output_file}.json")

    return(full_dict, file_list)
