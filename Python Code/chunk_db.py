import os, sys, glob, pickle, lzma, time, json
from tqdm import tqdm
from preprocess import prepare_PDF, prepare_text

allowed_texts = ['.txt', '.r', '.do', '.py', '.ipynb', '.sas', '.sql', '.vba', '.md']

def prepare_filelist(filepath, allowed_text_types = allowed_texts):
    """
    Scans the given directory recursively and collects all PDF and allowed text files.
    Calculates the total size of PDFs and text files in MB.

    Args:
        filepath (str): Path to the directory to scan.
        allowed_text_types (list): List of allowed text file extensions.

    Returns:
        dict: Contains lists of PDF and text files, and their total sizes in MB.
    """
    files = glob.glob(f"{filepath}/**/*", recursive=True)
    pdfs = [file for file in files if file.lower().endswith('.pdf')]
    t = []
    for i in allowed_text_types:
        t.append([file for file in files if file.lower().endswith(i)])
    texts = [ts for tss in t for ts in tss] # flatten the list of lists
    
    # total filesizes (in MB)
    pdf_size  = sum([os.path.getsize(i)/(1024**2) for i in pdfs])
    text_size = sum([os.path.getsize(i)/(1024**2) for i in texts])

    # Create an integer ID for each file path
    allowed_files = pdfs + texts
    id_lookup = {'filepath': allowed_files, 'file_id': list(range(len(allowed_files)))}

    return {'pdfs': pdfs, 'texts': texts, 'pdf_size': pdf_size, 'text_size': text_size}, id_lookup

def chunk_db(file_path
                      , output_file = "chunked_db"
                      , allowed_text_types = allowed_texts
                      , chunk_size=2056, chunk_overlap=16
                      ):
    """
    Processes all PDFs and allowed text files in the given directory.
    Chunks the files and periodically backs up the processed data.
    
    Args:
        file_path (str): Path to the directory to process.
        backup_file (str): Filename for backup pickle.
        allowed_text_types (list): List of allowed text file extensions.
        chunk_size (int): Size of each chunk.
        chunk_overlap (int): Overlap between chunks.

    Returns:
        dict: Dictionary containing processed chunks and file paths.
    """
    files, id_lookup = prepare_filelist(file_path, allowed_text_types)

    full_dict = {
        'processed_chunk': []
        , 'file_id': []
    }

    # Process PDFs
    if len(files['pdfs']) > 0:
        for file in tqdm(files['pdfs'], desc = "Chunking PDFs"):
            iter_dict = prepare_PDF(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)
            full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
            full_dict['file_id'].extend([id_lookup['file_id'][id_lookup['filepath'].index(file)]] * len(iter_dict['processed_chunk']))

    # Process text files
    if len(files['texts']) > 0:
        for file in tqdm(files['texts'], desc = "Chunking Text Files"):
            iter_dict = prepare_text(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)
            full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
            full_dict['file_id'].extend([id_lookup['file_id'][id_lookup['filepath'].index(file)]] * len(iter_dict['processed_chunk']))

    assert len(full_dict['processed_chunk']) > 0, "Found no files to analyze."

    # Add an id field which is just the number
    full_dict['chunk_id'] = list(range(len(full_dict['processed_chunk'])))

    # Export as JSON
    with open(f'../{output_file}.json', 'w', encoding='utf-8') as f:
        json.dump(full_dict, f, ensure_ascii=False, indent=2)

    # Export the file_path crosswalk for quick access
    with open(f'../{output_file}_id_lookup.json', 'w', encoding='utf-8') as f:
        json.dump(id_lookup, f, ensure_ascii=False, indent=2)

    print(f"Processed {len(full_dict['processed_chunk'])} chunks from {len(files['pdfs'])} PDFs and {len(files['texts'])} text files.")
    print(f"Data saved to ../{output_file}.json and ../{output_file}_id_lookup.json")

    return(full_dict, id_lookup)
