import pymupdf

# Faster chunker by approximating 1 word per 1 token. No tokenizer.

def setup_chunker(_chunk_size=256, _chunk_overlap=64):
    # Logic to adjust inputs if necessary

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
        end = chunk_size-1

        while end < len(words):
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)

            start = end - chunk_overlap + 1
            end = end + chunk_overlap
        
        # make sure the last chunk has all the remaining words
        if end < len(words) - 1:
            chunks.append(' '.join(words[end:]))

        return(chunks)

    return(chunker)

# Stop Words: common english words that don't add information content
stop_words = [
      'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves'
    , 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours'
    , 'yourself', 'yourselves', 'he', 'him', 'his', 'himself'
    , 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself'
    , 'they', 'them', 'their', 'theirs', 'themselves', 'what'
    , 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were'
    , 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did'
    , 'doing', 'a', 'an', 'the', 'and', 'because'
    , 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about'
    , 'from', 'so', 'very', 'should', "should've"
    ]

# Drop words: other words/symbols that should be removed
drop_words = [
    '@','&',"\n","\r","©", "\t","®","ø","•","◦","¿","¡","#","^","&","`","~",";",":"
    , "NBER WORKING PAPER SERIES"
    , "NATIONAL BUREAU OF ECONOMIC RESEARCH"
    , "National Bureau of Economic Research"
    , "ABSTRACT"
]

# Preprocessing function for PDFs
def preprocess(text):
    # Connect words across lines
    text = text.replace('-\n', '')

    # Drop words we don't care about where the symbol appears, doesn't need spaces
    for word in drop_words:
        text = text.replace(f'{word}', ' ')

    for word in stop_words:
        word_upper = word.title()
        text = text.replace(f' {word} ', ' ')
        text = text.replace(f' {word_upper} ', ' ')

    text = text.replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
    text = text.replace(' .', '.')
    text = text.strip()
    return(text)

# Function to convert PDF to chunkable text
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

    # chunk the raw text
    chunker = setup_chunker(_chunk_size, _chunk_overlap)
    chunks = chunker(paper_one_string)

    # Organize chunks and processed chunks into a dictionary
    chunk_data = {
        'raw_chunk': [chunk for chunk in chunks]
        , 'processed_chunk': [preprocess(chunk) for chunk in chunks]
        , 'file_path': [in_path for chunk in chunks]
    }

    return(chunk_data)

# Function to convert text files to chunkable text
def prepare_text(in_path, _chunk_size=256, _chunk_overlap=64):
    # Assert that the file is a text format
    allowed_formats = ['.txt', '.r', '.do', '.py', '.sas', '.sql', '.vba']
    
    c=0
    for i in allowed_formats:
        if in_path.lower().endswith(i):
            c+=1
    assert c>0, "This is not a valid text file. Use a different function."
    
    doc = pymupdf.open(in_path, filetype='txt')

    # combine all pages into one list
    paper = []
    for page in doc:
        # extract text from page
        page_text = page.get_text()

        # append to paper
        paper.append(page_text)

    # convert list into string
    paper_one_string = ' '.join(paper)

    # chunk the raw text
    chunker = setup_chunker(_chunk_size, _chunk_overlap)
    chunks = chunker(paper_one_string)

    # Organize chunks and processed chunks into a dictionary
    chunk_data = {
        'raw_chunk': [chunk for chunk in chunks]
        , 'processed_chunk': [preprocess(chunk) for chunk in chunks]
        , 'file_path': [in_path for chunk in chunks]
    }

    return(chunk_data)