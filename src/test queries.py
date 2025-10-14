
from utils import *
from queries import *
from indexes import *
from initialize import *

repo = r"C:\Users\Steven\Documents\Python\Data\NBER 1000"

return_packet = initialize(
    path=repo,
    chunk_size=256,
    chunk_overlap=16,
    semantic_search=True
)

files = return_packet['files']
file_dict = return_packet['file_dict']
chunks = return_packet['chunks']
retriever = return_packet['bm25_retriever']
index = return_packet['ann_index']

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
