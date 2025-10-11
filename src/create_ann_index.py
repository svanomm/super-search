from model2vec import StaticModel
from tqdm import tqdm
import os, sys, pickle, lzma, time, json
import numpy as np
#import pynndescent as nn

allowed_texts = ['.txt', '.r', '.do', '.py', '.ipynb', '.sas', '.sql', '.vba', '.md']

def create_ann_index(chunk_db_path:str
                    , model_name = "minishlab/potion-retrieval-32M"
                    ):

    # Define the model
    model = StaticModel.from_pretrained(model_name)
    
    # Load the directory
    with open(chunk_db_path, 'r', encoding='utf-8') as f:
        full_dict = json.load(f)

    # Encode the chunks
    print("Encoding the text...")
    vecs = model.encode(full_dict['processed_chunk'], show_progress_bar=True)
    
    print("Converting vectors to list format...")
    with tqdm(total=1, desc="Processing vectors", unit="step") as pbar:
        full_dict['vector'] = [i for i in np.unstack(vecs)]
        pbar.update(1)

    print("Saving the database...")
    with tqdm(total=1, desc="Saving full database", unit="file") as pbar:
        with lzma.open('../full_database.pickle', 'wb') as f:
            pickle.dump(full_dict, f)
        pbar.update(1)
    print(f"Saved the full database to ../full_database.pickle.")
    
    # Create the nearest-neighbor index
    #print("Creating the nearest-neighbor index...")
    #index = nn.NNDescent(vecs, metric='cosine', #n_neighbors=10, compressed=True, verbose=True, #random_state=1234)
    #index.prepare() # preloads the operations so that future uses are faster

    # Pickle the nn data
    #print("Saving the nearest-neighbor index...")
    #with lzma.open('../nn_database.pickle', 'wb') as f:
    #    pickle.dump(index, f)
    #    print(f"Saved the NN data to ../nn_database.pickle.")

    n = len(full_dict['processed_chunk'])
    print(f"Done! Full database has {n} chunks encoded.")

    #return(full_dict, index)
    return(full_dict)