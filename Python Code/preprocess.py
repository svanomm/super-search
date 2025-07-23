import pymupdf
import os

# Faster chunker by approximating 1 word per 1 token. No tokenizer.
def setup_chunker(_chunk_size:int, _chunk_overlap:int):
    # Option to treat the entire document as 1 chunk
    if _chunk_size == False:
        _chunk_size = 999999999
    if 2 * _chunk_overlap > _chunk_size:
        _chunk_overlap = round(_chunk_size / 2)
        print(f"Warning: chunk overlap too large, setting to {_chunk_overlap}.")

    def chunker(text, chunk_size = _chunk_size, chunk_overlap = _chunk_overlap):
        # Split text into words
        words = text.split(' ')
        chunks = []
        if chunk_size > len(words):
            chunk_size = len(words)
        start = 0
        end = chunk_size  # Fixed: Remove the -1
        while end <= len(words):  # Fixed: Use <= since we're now using inclusive end
            chunk = ' '.join(words[start:end])  # This now correctly includes chunk_size words
            chunks.append(chunk)
            start = end - chunk_overlap
            end = start + chunk_size  # Fixed: Maintain consistent chunk size

        # Handle remaining words if any
        if start < len(words):
            chunks.append(' '.join(words[start:]))

        return(chunks)
    return(chunker)

# Drop words: other words/symbols that should be removed
drop_words = [
    '@','&',"\n","\r","©","\t","®","ø","•","◦","¿","¡","#","^","&","`","~",";",":"
    ,'_','|', '.','*','`'
]

# Preprocessing function for PDFs
def preprocess(text:str):
    # Connect words across lines
    text = text.replace('-\n', '')
    # Drop words we don't care about where the symbol appears, doesn't need spaces
    for word in drop_words:
        text = text.replace(f'{word}', ' ')
    # Removing double marks
    for i in [' ', '.', ',', '!', '?']:
        text = text.replace(f'{i}{i}', f'{i}').replace(f'{i}{i}', f'{i}')
    text = text.replace(' .', '.')
    text = text.strip()
    return(text)

# Function to convert PDF to chunkable text
def prepare_PDF(in_path:str, _chunk_size:int, _chunk_overlap:int):
    """
    Converts a PDF document into preprocessed text chunks for further analysis or embedding.
    
    This function reads a PDF file, extracts all text content, splits it into overlapping chunks
    of specified size, and preprocesses each chunk to clean and standardize the text.
    
    Parameters:
    -----------
    in_path : str
        File path to the PDF document to be processed
    _chunk_size : int
        Target size of each chunk in words (approximate tokens)
        Set to False to treat the entire document as one chunk
    _chunk_overlap : int
        Number of overlapping words between consecutive chunks to maintain context
    
    Returns:
    --------
    dict
        A dictionary containing:
        - 'processed_chunk': List of preprocessed text chunks
        - 'file_path': List of file paths (same path repeated for each chunk)
    """
    # Assert that the file is a PDF
    assert in_path.lower().endswith('.pdf'), "This is not a PDF file. Use a different function."
    if not os.path.isfile(in_path):
        raise FileNotFoundError(f"File not found: {in_path}")
    try:
        doc = pymupdf.open(in_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")

    try:
        paper_one_string = preprocess(' '.join([page.get_text() for page in doc]))
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

    # Initialize and apply the chunking strategy
    chunker = setup_chunker(_chunk_size, _chunk_overlap)
    chunks = chunker(paper_one_string)

    # Create a structured output with both processed chunks and source information
    chunk_data = {
        'processed_chunk': [chunk for chunk in chunks],  # Apply text cleaning to each chunk
        'file_path': [in_path for chunk in chunks]  # Track source document for each chunk
    }

    return(chunk_data)

# Function to convert text files to chunkable text
def prepare_text(in_path:str, _chunk_size:int, _chunk_overlap:int):
    """
    Converts a text document into preprocessed text chunks for further analysis or embedding.

    This function reads a text file, extracts all text content, splits it into overlapping chunks
    of specified size, and preprocesses each chunk to clean and standardize the text.
    
    Parameters:
    -----------
    in_path : str
        File path to the PDF document to be processed
    _chunk_size : int
        Target size of each chunk in words (approximate tokens)
        Set to False to treat the entire document as one chunk
    _chunk_overlap : int
        Number of overlapping words between consecutive chunks to maintain context
    
    Returns:
    --------
    dict
        A dictionary containing:
        - 'processed_chunk': List of preprocessed text chunks
        - 'file_path': List of file paths (same path repeated for each chunk)
    """
    if not os.path.isfile(in_path):
        raise FileNotFoundError(f"File not found: {in_path}")
    try:
        with open(in_path, 'r', encoding='utf-8') as file:
            doc = file.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read text file: {e}")

    # convert list into string
    paper_one_string = preprocess(doc)

    # chunk the raw text
    chunker = setup_chunker(_chunk_size, _chunk_overlap)
    chunks = chunker(paper_one_string)

    # Organize chunks and processed chunks into a dictionary
    chunk_data = {
        'processed_chunk': [chunk for chunk in chunks]
        , 'file_path': [in_path for chunk in chunks]
    }

    return(chunk_data)
