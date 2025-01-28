from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import os, sys, glob, pickle
import pandas as pd
import numpy as np
import pynndescent as nn

# Add the current directory to the path
sys.path.append(os.getcwd())
from preprocess import prepare_PDF, prepare_text

def prepare_filelist(filepath, allowed_text_types = ['.txt', '.r', '.do', '.py', '.sas', '.sql', '.vba']):
    files = glob.glob(f"{filepath}/**/*", recursive=True)
    
    pdfs = [file for file in files if file.lower().endswith('.pdf')]
    
    t = []
    for i in allowed_text_types:
        t.append([file for file in files if file.lower().endswith(i)])
    
    texts = [ts for tss in t for ts in tss] # flatten the list of lists
    
    return {'pdfs': pdfs, 'texts': texts}

def prepare_directory(file_path, backup_file = "chunking_backup", allowed_text_types = ['.txt', '.r', '.do', '.py', '.sas', '.sql', '.vba']):
    files = prepare_filelist(file_path, allowed_text_types)

    full_dict = {
        'raw_chunk': []
        , 'processed_chunk': []
        , 'file_path': []
    }

    # Initiate the backup file
    with open(f'./{backup_file}.pickle', 'wb') as f:
        pickle.dump(full_dict, f)

    iters_per_dump = 20
    counter = 1
    
    # Process PDFs
    if len(files['pdfs']) > 0:
        for file in tqdm(files['pdfs'], desc = "Chunking PDFs"):
            iter_dict = prepare_PDF(file)
            full_dict['raw_chunk'].extend(iter_dict['raw_chunk'])
            full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
            full_dict['file_path'].extend(iter_dict['file_path'])

            counter+=1

            # Backup the data
            if counter % iters_per_dump == 0:
                with open(f'./{backup_file}.pickle', 'wb') as f:
                    pickle.dump(full_dict, f)
    
    # Process text files
    if len(files['texts']) > 0:
        for file in tqdm(files['texts'], desc = "Chunking Text Files"):
            iter_dict = prepare_text(file)
            full_dict['raw_chunk'].extend(iter_dict['raw_chunk'])
            full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
            full_dict['file_path'].extend(iter_dict['file_path'])
            
            counter+=1

            # Backup the data
            if counter % iters_per_dump == 0:
                with open(f'./{backup_file}.pickle', 'wb') as f:
                    pickle.dump(full_dict, f)

    assert len(full_dict['raw_chunk']) > 0, "Found no files to analyze."

    return(full_dict)

# Current encoding model implementation: static-retrieval-mrl-en-v1
# https://huggingface.co/sentence-transformers/static-retrieval-mrl-en-v1
# Model defaults to 1024 dense dimensions, but can be truncated to save space/time
truncated_dimensions = 1024
model = SentenceTransformer(
    "sentence-transformers/static-retrieval-mrl-en-v1"
    , device="cpu"
    , truncate_dim=truncated_dimensions
    )

def create_database(file_path
                    , model_name = "sentence-transformers/static-retrieval-mrl-en-v1"
                    , truncated_dimensions = 1024
                    , log_file = "chunking_log.txt"
                    , allowed_text_types = ['.txt', '.r', '.do', '.py', '.sas', '.sql', '.vba']
                    ):
    # Define the model
    model = SentenceTransformer(
        model_name
        , device="cpu"
        , truncate_dim=truncated_dimensions
        )
    
    # Prepare the directory
    print("Importing and processing files...")
    full_dict = prepare_directory(file_path, log_file, allowed_text_types)

    # Encode the chunks
    print("Encoding the text...")
    vecs = model.encode(full_dict['processed_chunk'])
    full_dict['vector'] = [i for i in np.unstack(vecs)]
    
    # Create the nearest-neighbor index
    print("Creating the nearest-neighbor index...")
    index = nn.NNDescent(vecs)
    index.prepare() # preloads the operations so that future uses are faster

    return(full_dict, index)