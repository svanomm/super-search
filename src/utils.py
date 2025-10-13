import pymupdf
import os, json, logging, hashlib, argparse, sys, json
from typing import Dict, Union, List
from datetime import datetime
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Faster chunker by approximating 1 word per 1 token. No tokenizer.
def setup_chunker(_chunk_size:int, _chunk_overlap:int):
    # Option to treat the entire document as 1 chunk
    if _chunk_size == False:
        _chunk_size = 999999999
    if 2 * _chunk_overlap > _chunk_size:
        _chunk_overlap = round(_chunk_size / 2)
        print(f"Warning: chunk overlap too large, setting to {_chunk_overlap}.")

    def chunker(text, chunk_size = _chunk_size, chunk_overlap = _chunk_overlap):
        # Split text into words
        words = text.split(' ')
        chunks = []
        if chunk_size > len(words):
            chunk_size = len(words)
        start = 0
        end = chunk_size  # Fixed: Remove the -1
        while end <= len(words):  # Fixed: Use <= since we're now using inclusive end
            chunk = ' '.join(words[start:end])  # This now correctly includes chunk_size words
            chunks.append(chunk)
            start = end - chunk_overlap
            end = start + chunk_size  # Fixed: Maintain consistent chunk size

        # Handle remaining words if any
        if start < len(words):
            chunks.append(' '.join(words[start:]))

        return(chunks)
    return(chunker)

UNICODE_WHITESPACE_CHARACTERS = [
    "\u0000", # null
    "\u0009", # character tabulation
    "\u000a", # line feed
    "\u000b", # line tabulation
    "\u000c", # form feed
    "\u000d", # carriage return
    "\u0020", # space
    "\u0085", # next line
    "\u00a0", # no-break space
    "\u1680", # ogham space mark
    "\u2000", # en quad
    "\u2001", # em quad
    "\u2002", # en space
    "\u2003", # em space
    "\u2004", # three-per-em space
    "\u2005", # four-per-em space
    "\u2006", # six-per-em space
    "\u2007", # figure space
    "\u2008", # punctuation space
    "\u2009", # thin space
    "\u200A", # hair space
    "\u2028", # line separator
    "\u2029", # paragraph separator
    "\u202f", # narrow no-break space
    "\u205f", # medium mathematical space
    "\u3000", # ideographic space
]

# Drop words: other words/symbols that should be removed
drop_words = [
    '@','&',"\n","\r","©","\t","®","ø","•","◦","¿","¡","#","^","&","`","~",";",":"
    ,'_','|', '.','*','`'
] + UNICODE_WHITESPACE_CHARACTERS

# Preprocessing function for PDFs
def preprocess(text:str):
    # Connect words across lines
    text = text.replace('-\n', '')
    # Drop words we don't care about where the symbol appears, doesn't need spaces
    for word in drop_words:
        text = text.replace(f'{word}', ' ')
    # Removing double marks
    for i in [' ', '.', ',', '!', '?']:
        text = text.replace(f'{i}{i}', f'{i}').replace(f'{i}{i}', f'{i}')
    text = text.replace(' .', '.')
    text = text.strip()
    return(text)

# Function to convert PDF to chunkable text
def prepare_PDF(in_path:str, _chunk_size:int, _chunk_overlap:int):
    """
    Converts a PDF document into preprocessed text chunks for further analysis or embedding.
    
    This function reads a PDF file, extracts all text content, splits it into overlapping chunks
    of specified size, and preprocesses each chunk to clean and standardize the text.
    
    Parameters:
    -----------
    in_path : str
        File path to the PDF document to be processed
    _chunk_size : int
        Target size of each chunk in words (approximate tokens)
        Set to False to treat the entire document as one chunk
    _chunk_overlap : int
        Number of overlapping words between consecutive chunks to maintain context
    
    Returns:
    --------
    list
        A list of preprocessed text chunks
    """
    # Assert that the file is a PDF
    assert in_path.lower().endswith('.pdf'), "This is not a PDF file. Use a different function."
    if not os.path.isfile(in_path):
        raise FileNotFoundError(f"File not found: {in_path}")
    try:
        doc = pymupdf.open(in_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")

    paper_one_string = ""
    # Iterate through each page and extract text
    try:
        counter=0
        #for page in tqdm(doc, desc="Extracting text from PDF"):
        for page in doc:
            try: 
                #print(f"Processing page {page.number + 1} of {len(doc)}")   
                # Extract text from each page
                page_text = page.get_text()
                if page_text:
                    paper_one_string += ' ' + page_text
            except Exception as e:
                logging.warning(f"Error processing file {in_path} page {page.number}: {e}")
                raise RuntimeError(f"Error processing file {in_path} page {page.number}: {e}")
    except Exception as e:
        logging.warning(f"Error processing file {in_path}: {e}")
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

    if paper_one_string == '':
        logging.warning(f"Empty PDF: {in_path}")
    else:
        # Initialize and apply the chunking strategy
        chunker = setup_chunker(_chunk_size, _chunk_overlap)
        return chunker(preprocess(paper_one_string))

# Function to chunk PDFs by page
def prepare_PDF_page(in_path:str):
    """
    Split a PDF document into text chunks by page for further analysis or embedding.

    This function reads a PDF file, extracts all text content, splits it into chunks
    by page, and preprocesses each chunk to clean and standardize the text.

    Parameters:
    -----------
    in_path : str
        File path to the PDF document to be processed
    
    Returns:
    --------
    dict
        A dictionary containing:
        - 'processed_chunk': List of preprocessed text chunks
        - 'page_number': List of page numbers corresponding to each chunk
    """
    # Assert that the file is a PDF
    assert in_path.lower().endswith('.pdf'), "This is not a PDF file. Use a different function."
    if not os.path.isfile(in_path):
        raise FileNotFoundError(f"File not found: {in_path}")
    try:
        doc = pymupdf.open(in_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")

    chunks = []
    pages = []
    # Iterate through each page and extract text
    try:
        for page in tqdm(doc, desc="Extracting text from PDF"):
            try: 
                #print(f"Processing page {page.number + 1} of {len(doc)}")   
                # Extract text from each page
                page_text = page.get_text()
                if page_text:
                    chunks.append(preprocess(page_text))
                    pages.append(page.number)
            except Exception as e:
                raise RuntimeError(f"Error processing page {page.number}: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

    # Create a structured output with both processed chunks and source information
    chunk_data = {
        'processed_chunk': chunks,
        'page_number': pages 
    }

    return(chunk_data)

# Function to convert text files to chunkable text
def prepare_text(in_path:str, _chunk_size:int, _chunk_overlap:int):
    """
    Converts a text document into preprocessed text chunks for further analysis or embedding.

    This function reads a text file, extracts all text content, splits it into overlapping chunks
    of specified size, and preprocesses each chunk to clean and standardize the text.
    
    Parameters:
    -----------
    in_path : str
        File path to the PDF document to be processed
    _chunk_size : int
        Target size of each chunk in words (approximate tokens)
        Set to False to treat the entire document as one chunk
    _chunk_overlap : int
        Number of overlapping words between consecutive chunks to maintain context
    
    Returns:
    --------
    list
        A list of text chunks
    """
    if not os.path.isfile(in_path):
        raise FileNotFoundError(f"File not found: {in_path}")
    try:
        with open(in_path, 'r', encoding='utf-8') as file:
            doc = file.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read text file: {e}")

    # convert list into string
    paper_one_string = preprocess(doc)

    # chunk the raw text
    chunker = setup_chunker(_chunk_size, _chunk_overlap)

    return chunker(paper_one_string)

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
                mod_time = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
                size = os.path.getsize(full_path)

                # Hash the file properties to uniquely identify it
                hash_id = hashlib.sha1(full_path.encode('utf-8')).hexdigest()

                # check if file-instance already in the list
                if hash_id in file_list['file_id']:
                    continue
                
                file_list['filepath'].append(full_path)
                file_list['last_modified'].append(mod_time)
                file_list['file_size'].append(int(size/(1024**2)))  # Size in MB
                file_list['date_added'].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                file_list['file_id'].append(hash_id)
            except (OSError, IOError) as e:
                # Skip files we can't access (permissions, etc.)
                logging.warning(f"Could not access {full_path}: {e}")
                continue
    logging.info("Done scanning.")

    if start_length > 0:
        added = len(file_list['filepath']) - start_length

    # Create a dict where file_id is the key and the element is another dict with the rest of the info
    file_dict = {file_list['file_id'][i]: {
        'filepath': file_list['filepath'][i],
        'last_modified': file_list['last_modified'][i],
        'file_size': file_list['file_size'][i],
        'date_added': file_list['date_added'][i]
    } for i in range(len(file_list['file_id']))}

    # Save to JSON files
    try:
        with open(output_filename, 'w') as f:
            json.dump(file_list, f, indent=2)
        with open("file_dict.json", 'w') as f:
            json.dump(file_dict, f, indent=2)
        if flag_existing == 0:
            logging.info(f"File list saved to {output_filename} with {len(file_list['filepath'])} files.")
        else:
            logging.info(f"File list updated in {output_filename} with {added} new files.")
    except IOError as e:
        logging.warning(f"Could not save to {output_filename}: {e}")

    return (file_list, file_dict)


default_chunk_size = 512
default_chunk_overlap = 32

def chunk_db(
        file_list_path:str = None
        , file_list = None
        , output_path = "./search_utils/chunked_db.json"
        , chunk_size=default_chunk_size, chunk_overlap=default_chunk_overlap
        , progress_callback=None
        ):

    # If given a file_list, don't load anything
    if file_list is None:
        if file_list_path is None:
            # Search for a default location
            try:
                with open("./search_utils/chunked_db.json", 'r') as f:
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
    for idx, file in enumerate(tqdm(file_list['filepath'], desc="Chunking files")):
        #logging.info(f"Processing file {idx + 1}/{len(file_list['filepath'])}: {file}")
        # Find the corresponding file_id
        f_id = file_list['file_id'][idx]

        # Confirm file exists
        if not os.path.exists(file):
            logging.warning(f"Warning: File {file} does not exist, skipping.")
            continue

        # determine file type
        if file.endswith('.pdf'):
            chunks = prepare_PDF(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)

        else:
            chunks = prepare_text(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)
        
        if chunks is not None:
            full_dict['processed_chunk'].extend(chunks)
            full_dict['file_id'].extend([f_id] * len(chunks))

        # Call the progress callback if provided
        #if progress_callback is not None:
        #    progress_callback(idx + 1)

    logging.info("Done processing files.")

    # Add a chunk id field which is just the number
    full_dict['chunk_id'] = list(range(len(full_dict['processed_chunk'])))

    # Export as JSON
    logging.info(f"Saving chunk database to file...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(full_dict, f, ensure_ascii=False, indent=2)

    logging.info(f"Processed {len(full_dict['processed_chunk'])} chunks from {len(file_list['filepath'])} files.")
    logging.info(f"Data saved to {output_path}")

    return full_dict

def chunk_db_page(
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
                with open("./search_utils/chunked_db.json", 'r') as f:
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
        , 'page_number': []
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
            iter_dict = {
                'processed_chunk': prepare_text(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)
            }
            iter_dict['page_number'] = [0] * len(iter_dict['processed_chunk'])
        
        full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
        full_dict['file_id'].extend([f_id] * len(iter_dict['processed_chunk']))
        full_dict['page_number'].extend(iter_dict['page_number'])

        # Call the progress callback if provided
        if progress_callback is not None:
            progress_callback(idx + 1)

    logging.info("Done processing files.")

    # Add a chunk id field which is just the number
    full_dict['chunk_id'] = list(range(len(full_dict['processed_chunk'])))

    # Export as JSON
    logging.info(f"Saving chunk database to file...")
    with open(f'./{output_file}.json', 'w', encoding='utf-8') as f:
        json.dump(full_dict, f, ensure_ascii=False, indent=2)

    logging.info(f"Processed {len(full_dict['processed_chunk'])} chunks from {len(file_list['filepath'])} files.")
    logging.info(f"Data saved to ./{output_file}.json")

    return full_dict

def convert_results(results, chunks, file_dict):
    """
    Convert search results results to include full chunk and file properties.
    Args:
        results (dict): The BM25 results with 'id' and 'score'.
        chunks (dict): The chunks data with 'processed_chunk', 'chunk_id', and 'file_id'.
        file_dict (dict): A dictionary mapping file_id to file properties.
    Returns:
        dict: A dictionary with full chunk and file properties.
    """
    results_full = {
        'processed_chunk': [chunks['processed_chunk'][i] for i in results['id']],
        'score': results['score'],
        'chunk_id': [chunks['chunk_id'][i] for i in results['id']],
        'file_id': [chunks['file_id'][i] for i in results['id']]
    }

    results_full['file_properties'] = [file_dict[i] for i in results_full['file_id']]

    return results_full
