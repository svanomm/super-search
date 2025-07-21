from model2vec import StaticModel
from tqdm import tqdm
import os, sys, pickle, lzma, time, json
import numpy as np
import pynndescent as nn

allowed_texts = ['.txt', '.r', '.do', '.py', '.ipynb', '.sas', '.sql', '.vba', '.md']

def create_ann_index(chunk_database
                    , model_name = "minishlab/potion-retrieval-32M"
                    , save_results = True
                    ):

    # Define the model
    model = StaticModel.from_pretrained(model_name)
    
    # Load the directory
    with open(chunk_database, 'r', encoding='utf-8') as f:
        full_dict = json.load(f)

    # Encode the chunks
    print("Encoding the text...")
    vecs = model.encode(full_dict['processed_chunk'], show_progress_bar=True)
    full_dict['vector'] = [i for i in np.unstack(vecs)]
    
    # Create the nearest-neighbor index
    print("Creating the nearest-neighbor index...")
    index = nn.NNDescent(vecs, metric='cosine', n_neighbors=10, compressed=True, verbose=True, random_state=1234)
    index.prepare() # preloads the operations so that future uses are faster

    print("Saving the database...")
    with lzma.open('../full_database.pickle', 'wb') as f:
        pickle.dump(full_dict, f)
        print(f"Saved the full database to ../full_database.pickle.")

    # Pickle the nn data
    print("Saving the nearest-neighbor index...")
    with lzma.open('../nn_database.pickle', 'wb') as f:
        pickle.dump(index, f)
        print(f"Saved the NN data to ../nn_database.pickle.")

    n = len(full_dict['processed_chunk'])
    print(f"Done! Full database has {n} chunks encoded.")

    return(full_dict, index)