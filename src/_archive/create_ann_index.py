from model2vec import StaticModel
from tqdm import tqdm
import os, sys, pickle, lzma, time, json
import numpy as np
import logging
import pynndescent as nn

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

allowed_texts = ['.txt', '.r', '.do', '.py', '.ipynb', '.sas', '.sql', '.vba', '.md']

def create_ann_index(chunk_db_path:str
                    , model_name = "minishlab/potion-retrieval-32M"
                    ):

    # Define the model
    model = StaticModel.from_pretrained(
        model_name,
        normalize=True,
        dimensionality=256,
        quantize_to="float16"
        ) # make sure these options work with your chosen model
    
    # Load the directory
    with open(chunk_db_path, 'r', encoding='utf-8') as f:
        full_dict = json.load(f)

    # Encode the chunks
    logger.info("Encoding the text...")
    vecs = model.encode(full_dict['processed_chunk'], show_progress_bar=True, max_length=None)
    
    logger.info("Converting vectors to list format...")
    with tqdm(total=1, desc="Processing vectors", unit="step") as pbar:
        full_dict['vector'] = [i for i in np.unstack(vecs)]
        pbar.update(1)

    logger.info("Saving the database...")
    with tqdm(total=1, desc="Saving full database", unit="file") as pbar:
        with lzma.open('./full_database.pickle', 'wb') as f:
            pickle.dump(full_dict, f)
        pbar.update(1)
    logger.info(f"Saved the vector database to ./full_database.pickle.")

    # Create the nearest-neighbor index
    logger.info("Creating the nearest-neighbor index...")
    index = nn.NNDescent(vecs, metric='cosine', n_neighbors=10, compressed=True, verbose=True, random_state=1234, low_memory=False)
    index.prepare() # preloads the operations so that future uses are faster

    # Pickle the nn data
    logger.info("Saving the nearest-neighbor index...")
    with lzma.open('./nn_database.pickle', 'wb') as f:
        pickle.dump(index, f)
        logger.info(f"Saved the NN data to ./nn_database.pickle.")

    n = len(full_dict['processed_chunk'])
    logger.info(f"Done! Full database has {n} chunks encoded.")

    return(full_dict, index)
    #return(full_dict)