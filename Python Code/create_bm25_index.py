"""
Module for creating and saving a BM25 index from a processed chunk database.
"""

import json, bm25s, Stemmer
from tqdm import tqdm

def create_bm25_index(chunk_db_path:str):
    """
    Loads a processed chunk database, tokenizes the corpus, creates a BM25 index,
    and saves the index to disk.

    Args:
        chunk_db_path (str): Path to the JSON file containing the processed chunk database.

    Returns:
        bm25s.BM25: The BM25 retriever object after indexing the corpus.
    """

    db = json.load(open(chunk_db_path, 'rb'))
    stemmer = Stemmer.Stemmer("english")

    # Tokenize the corpus
    corpus_tokens = bm25s.tokenize(
        db['processed_chunk'],
        stopwords="en",
        stemmer=stemmer,
        show_progress=True
        )
    
    # Create the BM25 model and index the corpus
    print("Creating BM25 index...")
    retriever = bm25s.BM25()
    
    # Add progress tracking for the indexing step
    with tqdm(total=1, desc="Indexing corpus", unit="step") as pbar:
        retriever.index(corpus_tokens)
        pbar.update(1)

    # Add progress tracking for the saving step
    print("Saving the BM25 index...")
    with tqdm(total=1, desc="Saving index to disk", unit="step") as pbar:
        retriever.save("index_bm25", corpus=db['processed_chunk'])
        pbar.update(1)

    return(retriever)