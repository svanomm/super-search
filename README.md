# Super Search

A powerful local semantic indexing and search tool for document repositories that combines traditional keyword search with advanced semantic search capabilities.

## Features

- **🔍 Hybrid Search**: Combines traditional BM25 keyword search with semantic search for comprehensive results
- **📄 Multi-format Support**: Supports PDF and text files with fast processing using PyMuPDF
- **🖥️ GUI Interface**: User-friendly graphical interface built with FreeSimpleGUI
- **⚡ Fast Performance**: Optimized for speed with approximate nearest neighbor search using pynndescent
- **🏠 Fully Local**: No internet connection required - all processing happens on your machine
- **📊 Advanced Chunking**: Custom chunking algorithm for optimal text processing
- **🔄 Real-time Indexing**: File scanning and index updating capabilities

## Technical Stack

- **PyMuPDF**: Fast PDF text extraction
- **bm25s**: BM25 keyword search implementation
- **pynndescent**: Approximate nearest neighbor search for semantic similarity
- **model2vec**: Efficient semantic embeddings
- **FreeSimpleGUI**: Cross-platform GUI framework

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/svanomm/super-search.git
   cd super-search
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Navigate to the Python Code directory**:
   ```bash
   cd "Python Code"
   ```

## Usage

### GUI Application

Launch the graphical interface:
```bash
python gui_frontend.py
```

The GUI provides three main tabs:
- **Input Tab**: Create and manage search indices
- **Search Tab**: Perform searches on indexed documents
- **Logging Tab**: View application logs and debug information

### Command Line Interface

For testing and development, use the CLI demo:
```bash
python cli_search_demo.py
```

### Basic Workflow

1. **Index Your Documents**:
   - Open the GUI application
   - Go to the "Input" tab
   - Select the folder containing your documents
   - Choose whether to create semantic indices
   - Click "Build Index"

2. **Search Your Documents**:
   - Go to the "Search" tab
   - Enter your search query
   - View results with relevant text snippets
   - Click on results for more details

## Project Structure

```
super-search/
├── Python Code/
│   ├── gui_frontend.py          # Main GUI application
│   ├── gui_backend.py           # GUI backend logic
│   ├── cli_search_demo.py       # Command line interface
│   ├── file_scanner.py          # File discovery and scanning
│   ├── chunk_db.py             # Text chunking and database
│   ├── create_bm25_index.py    # BM25 index creation
│   ├── create_ann_index.py     # Semantic index creation
│   ├── query_bm25.py           # BM25 search queries
│   ├── query_nn.py             # Semantic search queries
│   ├── preprocess.py           # Text preprocessing
│   └── test_gui_integration.py # Integration tests
├── data/                        # Test data and examples
├── index_bm25/                 # BM25 index storage
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Examples

### Searching for Machine Learning Content
```bash
# In the GUI search tab or CLI:
Query: "machine learning algorithms"
```

Results will include both exact keyword matches and semantically similar content about AI, neural networks, and data science.

### Technical Document Search
```bash
Query: "database optimization performance"
```

Finds documents discussing database tuning, query optimization, and performance analysis.

## Configuration

The application automatically handles most configuration, but you can customize:

- **Index Location**: Specify custom paths for storing search indices
- **Semantic Search**: Enable/disable semantic indexing for faster or more comprehensive search
- **File Types**: Currently supports PDF and text files (more formats planned)

## Development Status

### Completed ✅
- ~~Use PyMuPDF for faster file reads~~
- ~~Add support for text file reading~~
- ~~Implement custom chunking algorithm~~
- ~~Switch to approximate NN search (pynndescent) for fast queries~~
- ~~Add BM25 search as a complement to semantic search~~
- ~~Add a GUI~~

### In Progress 🚧
- Functionality for both top-n file retrieval as well as chunk-specific searching
- Scan working directory for newly added/changed files that can be updated in the search indices
- Create Windows executable

### Planned 📋
- Add OCR function (tesseract) for non-searchable PDFs
- Integrate **MarkItDown** to allow for docx, xlsx, pptx file conversion
- Enhanced file format support
- Advanced search filters and sorting options

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

Run the integration tests:
```bash
python test_gui_integration.py
```

For development testing:
```bash
python cli_search_demo.py
```

## Motivation

The goal of this project is to provide an entirely local platform for both traditional **keyword** and **semantic** searching through many files. Unlike cloud-based solutions, Super Search keeps all your data private and works offline. We use optimized packages like **PyMuPDF**, **bm25s**, **pynndescent**, and **model2vec** to allow for fast retrieval on standard laptops without requiring specialized hardware.

## License

This project is open source. Please check the repository for license details.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/svanomm/super-search) and open an issue.
