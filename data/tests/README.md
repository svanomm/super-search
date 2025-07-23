# super-search
Semantic indexing tool for document repositories

# Motivation
The goal of this project is to provide an entirely local platform for both traditional **keyword** and **semantic** searching through many files. We use packages like **PyMuPDF**, **bm25s**, **pynndescent**, and **model2vec** to allow for fast retrieval on laptops.

## To-Do List:
- ~~Use PyMuPDF for faster file reads~~
- ~~Add support for text file reading~~
- ~~Implement custom chunking algorithm~~
- ~~Switch to approximate NN search (pynndescent) for fast queries~~
- Add BM25 search as a complement to semantic search (in progress)
- Functionality for both top-n file retrieval as well as chunk-specific searching
- Scan working directory for newly added/changed files that can be updated in the search indices (in progress)
- Add OCR function (tesseract) for non-searchable PDFs
- Integrate **MarkItDown** to allow for docx, xlsx, pptx file conversion.
- Add a GUI
- Create Windows executable
