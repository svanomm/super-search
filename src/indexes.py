import json, bm25s, Stemmer
import logging
from tqdm import tqdm
from model2vec import StaticModel
import os, sys, pickle, lzma, time, json
import numpy as np
import logging
import pynndescent as nn

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_bm25_index(
        chunk_db_path:str = None,
        chunks = None):
    """
    Loads a processed chunk database, tokenizes the corpus, creates a BM25 index,
    and saves the index to disk.

    Args:
        chunk_db_path (str): Path to the JSON file containing the processed chunk database.

    Returns:
        bm25s.BM25: The BM25 retriever object after indexing the corpus.
    """

    # If given a chunks db, don't load anything
    if chunks is None:
        if chunk_db_path is None:
            # Search for a default location index
            try:
                chunks = json.load(open("./search_utils/chunked_db.json", 'rb'))
            except Exception as e: 
                raise ValueError("Either chunk_db_path or chunks must be provided.")

        chunks = json.load(open(chunk_db_path, 'rb'))
    
    stemmer = Stemmer.Stemmer("english")

    # Tokenize the corpus
    corpus_tokens = bm25s.tokenize(
        chunks['processed_chunk'],
        stopwords="en",
        stemmer=stemmer,
        show_progress=True
        )
    
    # Create the BM25 model and index the corpus
    logger.info("Creating BM25 index...")
    retriever = bm25s.BM25()
    
    # Add progress tracking for the indexing step
    with tqdm(total=1, desc="Indexing corpus", unit="step") as pbar:
        retriever.index(corpus_tokens)
        pbar.update(1)

    # Add progress tracking for the saving step
    logger.info("Saving the BM25 index...")
    retriever.save("index_bm25")

    return(retriever)


def create_ann_index(
        chunk_db_path:str = None,
        chunks = None,
        model_name = "minishlab/potion-retrieval-32M"
    ):

    # If given a chunks db, don't load anything
    if chunks is None:
        if chunk_db_path is None:
            # Search for a default location index
            try:
                chunks = json.load(open("./search_utils/chunked_db.json", 'rb'))
            except Exception as e: 
                raise ValueError("Either chunk_db_path or chunks must be provided.")

        chunks = json.load(open(chunk_db_path, 'r', encoding='utf-8'))

    # Define the model
    model = StaticModel.from_pretrained(
        model_name,
        normalize=True,
        dimensionality=256,
        quantize_to="float16",
        force_download=False
        ) # make sure these options work with your chosen model
    
    # Encode the chunks
    logger.info("Encoding the text...")
    vecs = model.encode(chunks['processed_chunk'], show_progress_bar=True, max_length=None)
    
    # Create the nearest-neighbor index
    logger.info("Creating the nearest-neighbor index...")
    index = nn.NNDescent(vecs, metric='cosine', n_neighbors=10, compressed=True, verbose=True, random_state=1234, low_memory=False, n_jobs=4)
    index.prepare() # preloads the operations so that future uses are faster

    # Pickle the nn data
    logger.info("Saving the nearest-neighbor index...")
    with open('./search_utils/nn_database.pkl', 'wb') as f:
        pickle.dump(index, f)
        logger.info(f"Saved the NN data to ./search_utils/nn_database.pkl.")

    return index
