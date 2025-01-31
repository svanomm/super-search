from multiprocessing import Pool
import pymupdf
from create_database import prepare_filelist
import time
from tqdm import tqdm

def prepare_PDF(in_path, _chunk_size=256, _chunk_overlap=64):
    # Assert that the file is a PDF
    assert in_path.lower().endswith('.pdf'), "This is not a PDF file. Use a different function."
    
    doc = pymupdf.open(in_path)

    # combine all pages into one list
    paper = []
    for page in doc:
        # extract text from page
        page_text = page.get_text()

        # append to paper
        paper.append(page_text)

    # convert list into string
    paper_one_string = ' '.join(paper)

    return(paper_one_string)

files = prepare_filelist(r"C:\Users\Steven\Documents\Python\Data\NBER 1000")
#print(len(files['pdfs'])) # 248

pymupdf.TOOLS.mupdf_display_errors(False) # ignore any PDF errors

if __name__ == '__main__':

    l = len(files['pdfs'])

    t0 = time.time()
    with Pool() as pool:
        results = pool.map(prepare_PDF, files['pdfs'])
    t = time.time() - t0
    print(f"Multiprocessing took {t} seconds for {l} files.")

    t0 = time.time()
    r=[]
    for file in tqdm(files['pdfs']):
        r.append(prepare_PDF(file))
    t = time.time() - t0
    print(f"Singlethreading took {t} seconds for {l} files.")