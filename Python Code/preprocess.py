from pypdf import PdfReader
from chonkie import SentenceChunker
from transformers import AutoTokenizer

def setup_chunker(_chunk_size=256, _chunk_overlap=64, _min_sentences_per_chunk=1, tokenizer_model = "google-bert/bert-base-uncased"):
    # Logic to adjust inputs if necessary
    if _chunk_size < 32:
        _chunk_size = 32
        print(f"Warning: chunk size too large, setting to {_chunk_size}.")

    if 2 * _chunk_overlap >= _chunk_size:
        _chunk_overlap = round(_chunk_size / 2)
        print(f"Warning: chunk overlap too large, setting to {_chunk_overlap}.")

    if _min_sentences_per_chunk < 1:
        _min_sentences_per_chunk = 1
        print(f"Warning: you tried to set minimum sentences to less than 1, setting to 1.")
    
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_model)

    chunker = SentenceChunker(
        tokenizer=tokenizer
        , chunk_size=_chunk_size
        , chunk_overlap=_chunk_overlap
        , min_sentences_per_chunk=_min_sentences_per_chunk
    )
    # Need to play around with these settings to see what the appropriate chunk is
    # Chunking too large would reduce accuracy, but chunking too small would generate too many vectors to search
    # Also need to experiment with overlap

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

# Preprocessing function
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
    text = text.strip()
    return(text)

# Function to convert PDF to chunkable text
def prepare_PDF(in_path, _chunk_size=256, _chunk_overlap=64, _min_sentences_per_chunk=1, tokenizer_model = "google-bert/bert-base-uncased"):
    reader = PdfReader(in_path)

    # combine all pages into one list
    paper = []
    for page in reader.pages:
        # extract text from page
        page_text = page.extract_text()

        # append to paper
        paper.append(page_text)

    # convert list into string
    paper_one_string = ' '.join(paper)

    # chunk the raw text
    chunker = setup_chunker(_chunk_size, _chunk_overlap, _min_sentences_per_chunk, tokenizer_model)
    chunks = chunker.chunk(paper_one_string)

    # Organize chunks and processed chunks into a dictionary
    chunk_data = {
        'raw_chunk': chunks
        , 'processed_chunk': []
    }

    for chunk in chunks:
        chunk_data['processed_chunk'].append(preprocess(chunk))

    return(chunk_data)