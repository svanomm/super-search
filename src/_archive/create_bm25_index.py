"""
Module for creating and saving a BM25 index from a processed chunk database.
"""

import json, bm25s, Stemmer
import logging
from tqdm import tqdm

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
                chunks = json.load(open("chunked_db.json", 'rb'))
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