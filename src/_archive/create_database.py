from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
from sentence_transformers.models import StaticEmbedding

import os
import sys
import glob
import pandas as pd
import numpy as np
import pynndescent as nn

glob.glob(r"C:\Users\Steven\Desktop", "*.pdf")

# Add the current directory to the path
sys.path.append(os.getcwd())
from preprocess import prepare_PDF

def prepare_filelist(file_path):
    files = os.listdir(papers_repo)

# Current encoding model implementation: static-retrieval-mrl-en-v1
# https://huggingface.co/sentence-transformers/static-retrieval-mrl-en-v1
# Model defaults to 1024 dense dimensions, but can be truncated to save space/time
truncated_dimensions = 1024
model = SentenceTransformer(
    "sentence-transformers/static-retrieval-mrl-en-v1"
    , device="cpu"
    , truncate_dim=truncated_dimensions
    )

## TESTING
# Importing a lot of PDFs to see how long this takes
papers_repo = r"C:\Users\Steven\Documents\Python\Data\NBER papers"

files = os.listdir(papers_repo)
files.sort(reverse=True)

full_dict = {
    'raw_chunk': []
    , 'processed_chunk': []
    , 'file_path': []
}

counter=1

for paper in files[0:100]:
    f = f"{papers_repo}/{paper}"
    iter_dict = prepare_PDF(f)
    full_dict['raw_chunk'].extend(iter_dict['raw_chunk'])
    full_dict['processed_chunk'].extend(iter_dict['processed_chunk'])
    full_dict['file_path'].extend(iter_dict['file_path'])
    if counter%5==0:
        print(f"Finished file {counter}.")
    counter+=1

df = pd.DataFrame.from_dict(full_dict)
df

# Currently takes around 1 second per file (with tokenization chunking)
# Takes ~ 0.7 seconds with approximate chunking
# After switching to PyMuPDF, 0.1 seconds per file, but 3 cmsOpenProfileFromMem errors

vecs = model.encode(df['processed_chunk'])
# This returns a np array of shape (n, d), where n is 
#     number of chunks and d is embedding dimensions.

df['vector'] = [i for i in np.unstack(vecs)]
# Add the embeddings to our dataframe in a single variable,
#     so each cell contains the d-dimensional np vector.

df
# takes 3-4 seconds