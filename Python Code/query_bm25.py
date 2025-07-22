import json, bm25s, Stemmer

def query_bm25(query:str
            , index_path:str
            , num_results:int = 3
            ):
    stemmer = Stemmer.Stemmer("english")

    ### Error checks
    num_results = 1 if num_results < 1 else num_results

    # Load the BM25 index
    retriever = bm25s.BM25.load(index_path, load_corpus=True, mmap=True)

    # Encode the query
    query_tokens = bm25s.tokenize(query, stopwords='en', stemmer=stemmer)

    results, scores = retriever.retrieve(query_tokens, k=num_results)
    
    results = {
        'text': [i['text'] for i in results[0]]
        , 'id': [i['id'] for i in results[0]]
    }

    return(results)
