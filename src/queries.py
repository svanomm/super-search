import json, bm25s, Stemmer, re, os, sys, pickle
from typing import List, Dict, Union
from utils import *
from model2vec import StaticModel
import numpy as np
import pynndescent

def query_bm25(query:str
            , index_path:str = None
            , retriever = None
            , num_results:int = 3
            ):
    """
    Retrieve the top-k most relevant documents for a given query using a BM25 index.

    Args:
        query (str): The search query string.
        index_path (str): Path to the BM25 index file.
        num_results (int, optional): Number of top results to return. Defaults to 3.

    Returns:
        dict: A dictionary with keys 'text' and 'id', each containing a list of results.
    """

    # If given a file_list, don't load anything
    if retriever is None:
        if index_path is None:
            # Search for a default location index
            try:
                retriever = bm25s.BM25.load("index_bm25", load_corpus=True, mmap=True)
            except Exception as e:
                raise ValueError("Either index_path or retriever must be provided.")

        # Load the BM25 index
        retriever = bm25s.BM25.load(index_path, load_corpus=True, mmap=True)

    stemmer = Stemmer.Stemmer("english")

    ### Error checks
    num_results = 1 if num_results < 1 else num_results

    # Encode the query
    query_tokens = bm25s.tokenize(preprocess(query), stopwords='en', stemmer=stemmer)

    r, s = retriever.retrieve(query_tokens, k=num_results)

    # normalize query scores to sum to 1
    scores = s[0].tolist()
    t=sum(scores)
    scores = [x / t for x in scores]
    
    results = {
        'id': r[0].tolist()
        , 'score': scores
    }

    return results

def query_direct(query: Union[str, re.Pattern]
                , chunk_db_path:str = None
                , chunks = None
                , num_results: int = 3
                , case_sensitive: bool = False
                , is_regex: bool = False
                ):
    """
    Search through text chunks using direct keyword matching or regular expressions.

    Args:
        query (str or re.Pattern): Search query string or compiled regex pattern.
        chunk_db_path (str, optional): Path to the chunked database JSON file.
        num_results (int, optional): Maximum number of results to return. Defaults to 3.
        case_sensitive (bool, optional): Whether search should be case-sensitive. Defaults to False.
        is_regex (bool, optional): Whether to treat query as a regular expression. Defaults to False.

    Returns:
        dict: A dictionary with keys 'id', 'score', 'chunk_text', and 'filepath',
              each containing a list of results.
    """
    
    ### Error checks
    num_results = 1 if num_results < 1 else num_results
    
    # If given a chunks db, don't load anything
    if chunks is None:
        if chunk_db_path is None:
            # Search for a default location index
            try:
                chunks = json.load(open("chunked_db.json", 'rb'))
            except Exception as e: 
                raise ValueError("Either chunk_db_path or chunks must be provided.")

        chunks = json.load(open(chunk_db_path, 'rb'))
    
    # Validate chunk database structure
    if 'processed_chunk' not in chunks or 'file_id' not in chunks:
        raise ValueError("Chunk database must contain 'processed_chunk' and 'file_id' keys.")

    # Prepare the search pattern
    if is_regex == True:
#        assert isinstance(query, re.Pattern), f"Invalid regular expression."
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags=flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}")
    else:
        # For simple string matching, escape special regex characters
        escaped_query = re.escape(preprocess(query))
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(escaped_query, flags=flags)
    
    # Search through chunks
    results = {'id': [], 'score': []}
    for idx, chunk_text in enumerate(chunks['processed_chunk']):
        # Find all matches in the chunk
        found_matches = pattern.findall(chunk_text)
        match_count = len(found_matches)
        if match_count > 0:
            # Calculate a relevance score based on match count
            results['id'].append(idx)
            results['score'].append(match_count)

    # Sort by score (descending) and id
    sorted_results = sorted(zip(results['id'], results['score']), key=lambda x: (-x[1], x[0]))

    # Limit to the top num_results
    sorted_results = sorted_results[:num_results]

    # normalize query scores to sum to 1
    scores = [r[1] for r in sorted_results]
    t=sum(scores)
    scores = [x / t for x in scores]

    # Format results to match the structure of other query functions
    results = {
        'id': [r[0] for r in sorted_results],
        'score': scores
    }

    return results

def query_nn(
        query:str, 
        index:pynndescent.pynndescent_.NNDescent = None,
        index_path:str = None,
        model_name:str = "minishlab/potion-retrieval-32M",
        num_results:int = 3,
        query_epsilon:float = 0.1
    ):

    # If given a file_list, don't load anything
    if index is None:
        if index_path is None:
            # Search for a default location index
            try:
                index = pickle.load(open("nn_database.pkl", 'rb'))
            except Exception as e:
                raise ValueError("Either index_path or index must be provided.")

        # Load the NN index
        index = pickle.load(open(index_path, 'rb'))

    ### Error checks
    num_results = 1 if num_results < 1 else num_results
    query_epsilon = 0.01 if query_epsilon < 0.01 else query_epsilon

    # Define the model. USE SAME OPTIONS AS IN create_ann_index.py
    model = StaticModel.from_pretrained(
        model_name,
        normalize=True,
        dimensionality=256,
        quantize_to="float16"
        ) # make sure these options work with your chosen model
    
    # Encode the query
    query_vec = model.encode(preprocess(query), max_length=None)
    id, score = index.query(query_vec.reshape(1,-1)
                          , k = num_results
                          , epsilon = query_epsilon)
    
    # normalize query scores to sum to 1
    scores = score.flatten().tolist()
    # NOTE: scores are distances, so lower is better
    inv_scores = [1 - s for s in scores]  # Invert scores for normalization. This works for cosine distance, but confirm if using a different metric.
    t=sum(inv_scores)
    inv_scores = [x / t for x in inv_scores]

    results = {
        'id': id.flatten().tolist()
        , 'score': inv_scores
    }

    return(results)
