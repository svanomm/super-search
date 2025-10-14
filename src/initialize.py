import os
import json
import pickle
import bm25s
from utils import *
from queries import *
from indexes import *

def load_existing_indices(path:str = None):
    """
    Load existing search indices from disk if they exist.
    
    This function checks for existing chunk database and search indices in the expected locations
    and attempts to load them. It returns information about what was successfully loaded.
    
    Args:
        path (str, optional): Root directory path where search_utils is located. 
                             If None, uses current working directory.
    
    Returns:
        dict: Dictionary containing:
            - 'success': Boolean indicating if at least chunk database was loaded
            - 'chunks': Loaded chunk database (None if not found)
            - 'files': Loaded file list (None if not found)
            - 'file_dict': Loaded file dictionary (None if not found)
            - 'bm25_retriever': Loaded BM25 index (None if not found)
            - 'ann_index': Loaded ANN index (None if not found)
            - 'has_chunks': Boolean
            - 'has_bm25': Boolean
            - 'has_ann': Boolean
            - 'messages': List of status messages
    """
    if path is None:
        path = os.getcwd()
    
    result = {
        'success': False,
        'chunks': None,
        'files': None,
        'file_dict': None,
        'bm25_retriever': None,
        'ann_index': None,
        'has_chunks': False,
        'has_bm25': False,
        'has_ann': False,
        'messages': []
    }
    
    # Check for chunk database
    chunk_db_path = os.path.join(path, 'search_utils', 'chunked_db.json')
    if os.path.exists(chunk_db_path):
        try:
            with open(chunk_db_path, 'r', encoding='utf-8') as f:
                result['chunks'] = json.load(f)
            result['has_chunks'] = True
            result['success'] = True
            result['messages'].append(f"✓ Loaded chunk database: {len(result['chunks']['chunk_id'])} chunks")
        except Exception as e:
            result['messages'].append(f"✗ Failed to load chunk database: {e}")
    else:
        result['messages'].append("✗ Chunk database not found")
    
    # Check for file list and file dict
    file_list_path = os.path.join(path, 'search_utils', 'file_list.json')
    if os.path.exists(file_list_path):
        try:
            with open(file_list_path, 'r', encoding='utf-8') as f:
                result['files'] = json.load(f)
            result['messages'].append(f"✓ Loaded file list: {len(result['files']['filepath'])} files")
        except Exception as e:
            result['messages'].append(f"✗ Failed to load file list: {e}")
    else:
        result['messages'].append("✗ File list not found")
    
    file_dict_path = os.path.join(path, 'search_utils', 'file_dict.json')
    if os.path.exists(file_dict_path):
        try:
            with open(file_dict_path, 'r', encoding='utf-8') as f:
                result['file_dict'] = json.load(f)
            result['messages'].append(f"✓ Loaded file dictionary")
        except Exception as e:
            result['messages'].append(f"✗ Failed to load file dictionary: {e}")
    else:
        result['messages'].append("✗ File dictionary not found")
    
    # Check for BM25 index
    bm25_index_path = os.path.join(path, 'search_utils', 'index_bm25')
    if os.path.exists(bm25_index_path):
        try:
            result['bm25_retriever'] = bm25s.BM25.load(bm25_index_path, load_corpus=True, mmap=True)
            result['has_bm25'] = True
            result['messages'].append("✓ Loaded BM25 index")
        except Exception as e:
            result['messages'].append(f"✗ Failed to load BM25 index: {e}")
    else:
        result['messages'].append("✗ BM25 index not found")
    
    # Check for ANN index
    ann_index_path = os.path.join(path, 'search_utils', 'nn_database.pkl')
    if os.path.exists(ann_index_path):
        try:
            with open(ann_index_path, 'rb') as f:
                result['ann_index'] = pickle.load(f)
            result['has_ann'] = True
            result['messages'].append("✓ Loaded ANN index")
        except Exception as e:
            result['messages'].append(f"✗ Failed to load ANN index: {e}")
    else:
        result['messages'].append("✗ ANN index not found")
    
    return result

def initialize(
        path:str = None,
        chunk_size:int = 256,
        chunk_overlap:int = 16,
        semantic_search:bool = True
        ):
    """
    Initialize a complete search system by scanning files, creating chunks, and building search indexes.
    
    This function performs a full initialization workflow: scans the specified directory for files,
    creates or updates a file list, processes files into text chunks, builds a BM25 keyword index,
    and optionally creates an ANN semantic search index. All artifacts are saved to a 'search_utils'
    subdirectory.

    Args:
        path (str, optional): Root directory path to scan for files. If None, uses current working directory.
        chunk_size (int, optional): Number of words per text chunk. Defaults to 256.
        chunk_overlap (int, optional): Number of overlapping words between consecutive chunks. Defaults to 16.
        semantic_search (bool, optional): Whether to create an ANN index for semantic search in addition
            to the BM25 index. Defaults to True.

    Returns:
        dict: Dictionary containing initialized components:
            - 'files': File list dictionary with metadata
            - 'file_dict': File dictionary keyed by file_id
            - 'chunks': Chunk database dictionary
            - 'bm25_retriever': BM25 index object for keyword search
            - 'ann_index': ANN index object for semantic search (only if semantic_search=True)

    Raises:
        NotADirectoryError: If the specified path is not a valid directory.
        
    Note:
        Creates a 'search_utils' subdirectory in the specified path to store all index files
        and databases. If an existing file list is found, new files are appended to it.
    """

    if path is None:
        path = os.getcwd()
        logging.info("You did not specify a path, so using the current working directory.")
    if not os.path.isdir(path):
        raise NotADirectoryError(f"The specified path is not a directory: {path}")

    os.chdir(path)
    
    # Create subdirectory called search_utils if it doesn't exist
    if not os.path.exists(f'{path}/search_utils'):
        os.makedirs(f'{path}/search_utils')
        logging.info(f"Created directory: {f'{path}/search_utils'}")

    # Check if file list exists in expected location
    if os.path.exists(f'{path}/search_utils/file_list.json'):
        logging.info("Found existing file list, updating results.")
        file_list_path = f'{path}/search_utils/file_list.json'
    else: # Create file list if it doesn't exist
        logging.info("Found no existing file list, creating results.")
        file_list_path = None
    
    files, file_dict = file_scanner(path, file_list_path=file_list_path)
    
    logging.info("Creating chunk database.")
    chunks = chunk_db(file_list=files, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    logging.info("Creating BM25 index.")
    bm25_retriever = create_bm25_index(chunks=chunks)

    if semantic_search:
        logging.info("Creating ANN index.")
        ann_index = create_ann_index(chunks=chunks)
    
    return_packet = {
        "files": files,
        "file_dict": file_dict,
        "chunks": chunks,
        "bm25_retriever": bm25_retriever
    }

    if semantic_search:
        return_packet["ann_index"] = ann_index

    return return_packet