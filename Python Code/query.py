from model2vec import StaticModel
from preprocess import preprocess
import pynndescent

def query(query:str, index:pynndescent.pynndescent_.NNDescent, chunks:dict
            , model_name:str = "minishlab/potion-retrieval-32M"
            , num_results:int = 3
            , query_epsilon:float = 0.1
            ):
    
    ### Error checks
    num_results = 1 if num_results < 1 else num_results
    query_epsilon = 0.01 if query_epsilon < 0.01 else query_epsilon

    # Define the model
    model = StaticModel.from_pretrained(model_name)
    
    # Encode the query
    query_vec = model.encode(query)
    vecs = index.query(query_vec.reshape(1,-1)
                          , k = num_results
                          , epsilon = query_epsilon)
    
    results = {
        'chunk_text': [chunks['processed_chunk'][i] for i in vecs[0][0]]
        ,'filepath':  [chunks['file_path'][i] for i in vecs[0][0]]
    }

    return(results)
