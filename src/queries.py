import json, bm25s, Stemmer, re, os, sys, pickle
from typing import List, Dict, Union
from utils import *
from model2vec import StaticModel
import numpy as np
import pynndescent
import heapq
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial

def query_bm25(query:str
            , index_path:str = None
            , retriever = None
            , num_results:int = 3
            ):
    """
    Retrieve the top-k most relevant text chunks using BM25 keyword-based search.
    
    This function performs full-text search using the BM25 ranking algorithm. The query is preprocessed,
    tokenized with English stopwords and stemming, and matched against the indexed corpus. Scores are
    normalized to sum to 1.

    Args:
        query (str): The search query string to find relevant documents.
        index_path (str, optional): Path to the BM25 index directory. If None and retriever is None,
            attempts to load from default location './search_utils/index_bm25'.
        retriever (bm25s.BM25, optional): Pre-loaded BM25 retriever object. If provided, index_path is ignored.
        num_results (int, optional): Maximum number of top results to return. Defaults to 3.
            Minimum value is 1.

    Returns:
        dict: Dictionary containing:
            - 'id': List of chunk IDs (indices) for the top results
            - 'score': List of normalized relevance scores (sum to 1)

    Raises:
        ValueError: If neither index_path nor retriever are provided and default location is not found.
    """

    # If given a file_list, don't load anything
    if retriever is None:
        if index_path is None:
            # Search for a default location index
            try:
                retriever = bm25s.BM25.load("./search_utils/index_bm25", load_corpus=True, mmap=True)
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

def _count_matches_chunk(idx_chunk_tuple, pattern, is_regex):
    """
    Count occurrences of a pattern in a single text chunk for parallel processing.
    
    This helper function is designed for use with multiprocessing to count matches
    in text chunks. It handles both regex patterns and simple string matching efficiently.
    
    Args:
        idx_chunk_tuple (tuple): Tuple containing (chunk_index, chunk_text).
        pattern (re.Pattern or str): Compiled regex pattern or lowercase query string for matching.
        is_regex (bool): If True, pattern is treated as a regex; if False, uses string counting.
    
    Returns:
        tuple or None: Tuple of (chunk_index, match_count) if matches found, None otherwise.
    """
    idx, chunk_text = idx_chunk_tuple
    
    if is_regex:
        # Use finditer for memory efficiency - only count matches
        match_count = sum(1 for _ in pattern.finditer(chunk_text))
    else:
        # Fast string counting for non-regex
        match_count = chunk_text.count(pattern)
    
    if match_count > 0:
        return (idx, match_count)
    return None

def query_direct(query: Union[str, re.Pattern]
                , chunk_db_path:str = None
                , chunks = None
                , num_results: int = 3
                , case_sensitive: bool = False
                , is_regex: bool = False
                , use_parallel: bool = True
                , max_workers: int = None
                ):
    """
    Search text chunks using direct keyword matching or regular expressions with optional parallel processing.
    
    This optimized function supports both simple string matching and complex regex patterns. It uses
    heap-based sorting for efficiency and can leverage multiprocessing for large databases with regex searches.
    Results are ranked by match count and scores are normalized to sum to 1.

    Args:
        query (str or re.Pattern): Search query string or compiled regex pattern to match in chunks.
        chunk_db_path (str, optional): Path to the chunked database JSON file. If None and chunks is None,
            attempts to load from default location './search_utils/chunked_db.json'.
        chunks (dict, optional): Pre-loaded chunks dictionary containing 'processed_chunk' and 'file_id' keys.
            If provided, chunk_db_path is ignored.
        num_results (int, optional): Maximum number of top results to return. Defaults to 3. Minimum value is 1.
        case_sensitive (bool, optional): Whether search should be case-sensitive. Defaults to False.
        is_regex (bool, optional): Whether to treat query as a regular expression. Defaults to False.
        use_parallel (bool, optional): Enable multiprocessing for parallel search. Only used for databases
            with >1000 chunks. Defaults to True.
        max_workers (int, optional): Number of parallel worker processes. Defaults to CPU count if None.

    Returns:
        dict: Dictionary containing:
            - 'id': List of chunk IDs (indices) for the top results
            - 'score': List of normalized match count scores (sum to 1)

    Raises:
        ValueError: If neither chunk_db_path nor chunks are provided and default location is not found,
            if chunk database structure is invalid, or if regex pattern is invalid.
    """
    
    ### Error checks
    num_results = 1 if num_results < 1 else num_results
    
    # If given a chunks db, don't load anything
    if chunks is None:
        if chunk_db_path is None:
            # Search for a default location index
            try:
                chunks = json.load(open("./search_utils/chunked_db.json", 'rb'))
            except Exception as e: 
                raise ValueError("Either chunk_db_path or chunks must be provided.")

        chunks = json.load(open(chunk_db_path, 'rb'))
    
    # Validate chunk database structure
    if 'processed_chunk' not in chunks or 'file_id' not in chunks:
        raise ValueError("Chunk database must contain 'processed_chunk' and 'file_id' keys.")

    # Prepare the search pattern
    if is_regex == True:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags=flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}")
    else:
        # For simple string matching - prepare pattern based on case sensitivity
        if case_sensitive:
            # For case-sensitive non-regex, use plain string
            pattern = preprocess(query)
        else:
            # For case-insensitive non-regex, use fast string method
            # Store lowercase version of query for fast counting
            pattern = preprocess(query).lower()
    
    # Determine if we should use parallel processing
    # Only use parallel for large databases and regex searches
    num_chunks = len(chunks['processed_chunk'])
    use_parallel = use_parallel and num_chunks > 1000
    
    # Search through chunks
    results_list = []
    
    if use_parallel and is_regex:
        # Parallel processing for regex searches on large databases
        chunk_enum = list(enumerate(chunks['processed_chunk']))
        
        # Use ProcessPoolExecutor for CPU-bound regex operations
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Create partial function with pattern
            search_func = partial(_count_matches_chunk, pattern=pattern, is_regex=is_regex)
            
            # Submit all chunks for processing
            futures = {executor.submit(search_func, item): item for item in chunk_enum}
            
            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    results_list.append(result)
    else:
        # Sequential processing for non-regex or small databases
        for idx, chunk_text in enumerate(chunks['processed_chunk']):
            if is_regex:
                # Use finditer for memory efficiency - only count matches
                match_count = sum(1 for _ in pattern.finditer(chunk_text))
            else:
                # Fast string counting for non-regex case-insensitive
                if case_sensitive:
                    match_count = chunk_text.count(pattern)
                else:
                    match_count = chunk_text.lower().count(pattern)
            
            if match_count > 0:
                results_list.append((idx, match_count))
    
    # If no results found, return empty structure
    if not results_list:
        return {'id': [], 'score': []}
    
    # Use heap to get top num_results efficiently (O(n log k) instead of O(n log n))
    if len(results_list) <= num_results:
        # If we have fewer results than requested, use all of them
        top_results = sorted(results_list, key=lambda x: (-x[1], x[0]))
    else:
        # Use nlargest for efficient partial sorting
        top_results = heapq.nlargest(num_results, results_list, key=lambda x: (x[1], -x[0]))
        # Sort by score descending, then by id ascending
        top_results = sorted(top_results, key=lambda x: (-x[1], x[0]))

    # normalize query scores to sum to 1
    scores = [r[1] for r in top_results]
    t = sum(scores)
    scores = [x / t for x in scores]

    # Format results to match the structure of other query functions
    results = {
        'id': [r[0] for r in top_results],
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
    """
    Perform semantic similarity search using Approximate Nearest Neighbor (ANN) index.
    
    This function encodes the query using a Model2Vec static embedding model and searches for the
    most semantically similar chunks using cosine distance. The query is preprocessed before encoding.
    Scores are inverted (since lower distance is better) and normalized to sum to 1.

    Args:
        query (str): The search query string to find semantically similar documents.
        index (pynndescent.NNDescent, optional): Pre-loaded nearest neighbor index. If provided, index_path is ignored.
        index_path (str, optional): Path to the pickled NN index file. If None and index is None,
            attempts to load from default location './search_utils/nn_database.pkl'.
        model_name (str, optional): Name of the Model2Vec embedding model to use. Must match the model
            used during index creation. Defaults to "minishlab/potion-retrieval-32M".
        num_results (int, optional): Maximum number of top results to return. Defaults to 3. Minimum value is 1.
        query_epsilon (float, optional): Search accuracy parameter for ANN algorithm. Lower values are more accurate
            but slower. Defaults to 0.1. Minimum value is 0.01.

    Returns:
        dict: Dictionary containing:
            - 'id': List of chunk IDs (indices) for the most similar results
            - 'score': List of normalized inverted distance scores (sum to 1, higher is more similar)

    Raises:
        ValueError: If neither index_path nor index are provided and default location is not found.
        
    Note:
        Model configuration (normalize, dimensionality, quantize_to) must match the settings used
        during index creation for consistent results.
    """

    # If given a file_list, don't load anything
    if index is None:
        if index_path is None:
            # Search for a default location index
            try:
                index = pickle.load(open("./search_utils/nn_database.pkl", 'rb'))
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
        quantize_to="float16",
        force_download=False
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
