
from utils import *
from queries import *
from indexes import *

repo = r"C:\Users\Steven\Documents\Python\Data\NBER 1000"

files, file_dict = file_scanner(repo)

chunks = chunk_db(file_list=files, chunk_size=256, chunk_overlap=16)

retriever = create_bm25_index(chunks=chunks)
index = create_ann_index(chunks=chunks)

text = "Current Population Survey (CPS)"

results_bm25 = query_bm25(
    query = text,
    retriever=retriever,
    num_results=20)

results_direct = query_direct(
    query = text,
    chunks=chunks,
    num_results=20)

results_nn = query_nn(
    query = text,
    index=index,
    num_results=20)
    
print(results_bm25)
print(results_direct)
print(results_nn)
