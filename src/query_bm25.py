import json, bm25s, Stemmer

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
    query_tokens = bm25s.tokenize(query, stopwords='en', stemmer=stemmer)

    r, s = retriever.retrieve(query_tokens, k=num_results)
    
    results = {
        'id': r[0].tolist()
        , 'score': s[0].tolist()
    }

    return(results)


if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description="Query BM25 index")
    parser.add_argument("query", help="query string")
    parser.add_argument("--index_path", "-i", help="path to BM25 index", default="index_bm25")
    parser.add_argument("--num_results", "-n", type=int, default=3)
    args = parser.parse_args()

    try:
        results = query_bm25(args.query, index_path=args.index_path, num_results=args.num_results)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    print(json.dumps(results))
