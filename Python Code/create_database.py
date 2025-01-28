from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import os, sys, glob, pickle, json, lzma, time
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

def prepare_directory(file_path
                      , backup_file = "chunking_backup"
                      , allowed_text_types = ['.txt', '.r', '.do', '.py', '.sas', '.sql', '.vba']
                      , chunk_size=256, chunk_overlap=64
                      ):
    files = prepare_filelist(file_path, allowed_text_types)

    full_dict = {
        'raw_chunk': []
        , 'processed_chunk': []
        , 'file_path': []
    }

    # Initiate the backup file
    with open(f'../{backup_file}.pickle', 'wb') as f:
        pickle.dump(full_dict, f)

    iters_per_dump = 500
    counter = 1
    
    # Process PDFs
    if len(files['pdfs']) > 0:
        for file in tqdm(files['pdfs'], desc = "Chunking PDFs"):
            iter_dict = prepare_PDF(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)
            full_dict['raw_chunk'].extend(iter_dict['raw_chunk'])
            full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
            full_dict['file_path'].extend(iter_dict['file_path'])

            counter+=1

            # Backup the data
            if counter % iters_per_dump == 0:
                with open(f'../{backup_file}.pickle', 'wb') as f:
                    pickle.dump(full_dict, f)
    
    # Process text files
    if len(files['texts']) > 0:
        for file in tqdm(files['texts'], desc = "Chunking Text Files"):
            iter_dict = prepare_text(file, _chunk_overlap=chunk_overlap, _chunk_size=chunk_size)
            full_dict['raw_chunk'].extend(iter_dict['raw_chunk'])
            full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
            full_dict['file_path'].extend(iter_dict['file_path'])
            
            counter+=1

            # Backup the data
            if counter % iters_per_dump == 0:
                with open(f'../{backup_file}.pickle', 'wb') as f:
                    pickle.dump(full_dict, f)

    assert len(full_dict['raw_chunk']) > 0, "Found no files to analyze."

    with lzma.open(f'../{backup_file}.pickle', 'wb') as f:
        pickle.dump(full_dict, f)

    return(full_dict)

# Current encoding model implementation: static-retrieval-mrl-en-v1
# https://huggingface.co/sentence-transformers/static-retrieval-mrl-en-v1
# Model defaults to 1024 dense dimensions, but can be truncated to save space/time

def create_database(file_path
                    , model_name = "sentence-transformers/static-retrieval-mrl-en-v1"
                    , backup_file = "chunking_backup"
                    , truncated_dimensions = 1024
                    , allowed_text_types = ['.txt', '.r', '.do', '.py', '.sas', '.sql', '.vba']
                    , save_results = True
                    , chunk_size=256, chunk_overlap=64
                    ):
    # Define the model
    model = SentenceTransformer(
        model_name
        , device="cpu"
        , truncate_dim=truncated_dimensions
        )
    
    # Prepare the directory
    print("Importing and processing files...")
    t0 = time.time()
    full_dict = prepare_directory(file_path, backup_file, allowed_text_types, chunk_overlap=chunk_overlap, chunk_size=chunk_size)
    t = round(time.time() - t0)
    print(f"Done. Took {t} seconds.")

    # Encode the chunks
    print("Encoding the text...")
    t0 = time.time()
    vecs = model.encode(full_dict['processed_chunk'])
    full_dict['vector'] = [i for i in np.unstack(vecs)]
    t = round(time.time() - t0)
    print(f"Done. Took {t} seconds.")
    
    # Create the nearest-neighbor index
    print("Creating the nearest-neighbor index...")
    t0 = time.time()
    index = nn.NNDescent(vecs)
    index.prepare() # preloads the operations so that future uses are faster
    t = round(time.time() - t0)
    print(f"Done. Took {t} seconds.")

    # don't need to save the processed text
    full_dict_small = {
        'raw_chunk'  : full_dict['raw_chunk']
        , 'file_path': full_dict['file_path']
        , 'vector'   : full_dict['vector']
    }
    
    print("Saving the database...")
    t0 = time.time()
    with lzma.open('../full_database.pickle', 'wb') as f:
        pickle.dump(full_dict_small, f)
        t = round(time.time() - t0)
        print(f"Saved the full database to ../full_database.pickle. Took {t} seconds.")

    # Pickle the nn data
    print("Saving the nearest-neighbor index...")
    t0 = time.time()
    with lzma.open('../nn_database.pickle', 'wb') as f:
        pickle.dump(index, f)
        t = round(time.time() - t0)
        print(f"Saved the NN data to ../nn_database.pickle. Took {t} seconds.")

    return(full_dict, index)