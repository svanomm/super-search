import json, bm25s, Stemmer

def create_bm25_index(chunk_db_path:str):

    db = json.load(open('chunked_db.json', 'rb'))
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