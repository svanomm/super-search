from sentence_transformers import SentenceTransformer
from preprocess import preprocess
import pynndescent

def query(query:str, index:pynndescent.pynndescent_.NNDescent, chunks:dict
            , model_name:str = "sentence-transformers/static-retrieval-mrl-en-v1"
            , truncated_dimensions:int = 1024
            , num_results:int = 3
            , query_epsilon:float = 0.1
            ):
    
    ### Error checks
    assert truncated_dimensions >= 1, "You tried to encode into < 1 dimensions."
    num_results = 1 if num_results < 1 else num_results
    query_epsilon = 0.01 if query_epsilon < 0.01 else query_epsilon

    truncated_dimensions = index.dim if truncated_dimensions != index.dim else truncated_dimensions

    # Define the model
    model = SentenceTransformer(
        model_name
        , device="cpu"
        , truncate_dim=truncated_dimensions
        )
    
    # Encode the query
    query_vec = model.encode(query)
    vecs = index.query(query_vec.reshape(1,-1)
                          , k = num_results
                          , epsilon = query_epsilon)
    
    results = {
        'chunk_text': [chunks['raw_chunk'][i] for i in vecs[0][0]]
        ,'filepath':  [chunks['file_path'][i] for i in vecs[0][0]]
    }

    return(results)
