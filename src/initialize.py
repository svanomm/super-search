import os
from utils import *
from queries import *
from indexes import *

def initialize(
        path:str = None,
        chunk_size:int = 256,
        chunk_overlap:int = 16,
        semantic_search:bool = True
        ):

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
        logging.info("Found existing file list, appending results.")
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