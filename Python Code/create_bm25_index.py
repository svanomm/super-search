"""
Module for creating and saving a BM25 index from a processed chunk database.
"""

import json, bm25s, Stemmer

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
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    print("Saving the database...")
    retriever.save("index_bm25", corpus=db['processed_chunk'])

    return(retriever)