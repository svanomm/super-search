# Interactive CLI Guide

## Quick Start

1. **Activate the virtual environment**:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **Run the CLI**:
   ```bash
   # Normal mode (clean output, no debug logs)
   python cli.py
   
   # Verbose mode (with debug/logging output)
   python cli.py --verbose
   # or
   python cli.py -v
   ```

3. **Initialization Flow**:
   - Select directory to search
   - Check for existing indices
   - Choose mode (Simplified or Advanced)
   - Configure settings based on mode
   - Start searching!

## Mode Comparison

| Feature | Simplified Mode | Advanced Mode |
|---------|----------------|---------------|
| **Setup** | One-click with defaults | Full customization |
| **Directory Selection** | Current directory only | Choose any directory |
| **Chunk Size** | Fixed at 256 words | Customizable |
| **Chunk Overlap** | Fixed at 16 words | Customizable |
| **Search Types** | BM25 only | BM25, Direct/Regex, Semantic |
| **Results Per Query** | Fixed at 5 | Customizable |
| **Search Options** | None (all defaults) | Case sensitivity, regex, epsilon |
| **Best For** | Quick searches, new users | Complex queries, power users |

## Simplified Mode

### Features
- **Zero Configuration**: Uses sensible defaults for everything
- **Fast Initialization**: No semantic search = faster setup
- **Streamlined Search**: Just enter your query and get 5 BM25 results
- **Perfect For**: 
  - First-time users
  - Quick document searches
  - Finding specific terms or phrases

### Simplified Mode Workflow

```
1. Start CLI → Main Menu
2. Initialize system
   a. Choose directory
   b. Check for existing indices (use if available)
   c. If building new: Select Simplified Mode
   d. Confirm defaults
3. Search: Type query → Get 5 results → Repeat
4. Type 'back' to return to main menu
```

### Simplified Mode Example
```
--- MAIN MENU ---
Status: System not initialized

1. Initialize system
2. Exit

Select option (1-2): 1

--- SYSTEM INITIALIZATION ---

Current directory: C:\Users\Steven\Documents\MyDocs
Use current directory? (y/n) [default: y]: y

Selected directory: C:\Users\Steven\Documents\MyDocs

Checking for existing search indices...
✗ Chunk database not found
✗ File list not found
✗ File dictionary not found
✗ BM25 index not found
✗ ANN index not found

This will scan your documents and create search indexes.

--- MODE SELECTION ---

Choose your interface mode:

1. Simplified Mode
   - Quick setup with default settings
   - BM25 keyword search only
   - Returns 5 results per query
   - Best for: Quick searches and new users

2. Advanced Mode
   - Full control over all settings
   - Multiple search types (BM25, Direct/Regex, Semantic)
   - Customizable parameters
   - Best for: Power users and complex queries

Select mode (1-2): 1

✓ Simplified mode selected

Using directory: C:\Users\Steven\Documents\MyDocs
Using default settings:
  - Chunk size: 256 words
  - Chunk overlap: 16 words
  - Search type: BM25 keyword search only

Proceed with initialization? (y/n) [default: y]: y

[System initializes...]

--- MAIN MENU ---
Status: System initialized ✓ (Simplified Mode)

1. Perform search
2. Re-initialize system
3. Exit

Select option (1-3): 1

--- SEARCH ---
Using: BM25 keyword search, 5 results

Enter 'back' to return to main menu

Enter your search query: machine learning

[Results displayed...]

Enter your search query: neural networks

[Results displayed...]

Enter your search query: back

--- MAIN MENU ---
```

## Advanced Mode

### Features

### Initialization Wizard
The CLI guides you through setting up your search system with these options:

- **Load Existing Indices**: If you've previously initialized the system, you can quickly reload existing indices
  - Checks for existing chunk database, BM25 index, and ANN index in `./search_utils/`
  - Much faster than re-scanning all documents
  - Shows which indices are available and missing
  - Can proceed even if some indices are missing (with limited functionality)
- **Directory Selection**: Choose which folder to scan for documents
- **Chunk Size**: Number of words per text chunk (default: 256)
  - Smaller chunks = more precise results but more chunks
  - Larger chunks = more context but less precise
- **Chunk Overlap**: Overlapping words between chunks (default: 16)
  - Helps maintain context across chunk boundaries
- **Semantic Search**: Enable AI-powered meaning-based search
  - Slower but more intelligent than keyword search
  - Optional - disable for faster initialization

### Search Types

#### 1. BM25 Search (Keyword-Based)
- Fast traditional keyword search
- Uses BM25 ranking algorithm
- Best for: exact terms, names, specific phrases
- Example: "machine learning" finds documents with those words

#### 2. Direct Search (Exact/Regex)
- Pattern matching search
- Options:
  - **Case Sensitive**: Match exact capitalization
  - **Regex**: Use regular expressions for complex patterns
- Best for: specific patterns, code snippets, formatted data
- Examples:
  - Exact: "Chapter 1" finds exact phrase
  - Regex: `\d{4}-\d{2}-\d{2}` finds dates like 2025-10-13

#### 3. Semantic Search (AI-Powered)
- Meaning-based search using embeddings
- Finds conceptually similar content
- Adjustable accuracy with epsilon parameter:
  - Lower epsilon (0.01) = more accurate, slower
  - Higher epsilon (0.5-1.0) = faster, less accurate
- Best for: concepts, ideas, related topics
- Example: "artificial intelligence" also finds "machine learning", "neural networks"

### Result Display

Each result shows:
- **Score**: Relevance score (normalized to sum to 1)
- **File Path**: Location of the source document
- **Last Modified**: When the file was last updated
- **Chunk ID**: Internal identifier for the text chunk
- **Text Preview**: First 300 characters of the matching text

## Example Session

### First-Time Initialization
```
======================================================================
                    SUPER SEARCH - Local Search Engine
======================================================================

--- MAIN MENU ---
Status: System not initialized

1. Initialize system
2. Exit

Select option (1-2): 1

--- SYSTEM INITIALIZATION ---

Current directory: C:\Users\Steven\Documents\MyDocs
Use current directory? (y/n) [default: y]: y

Selected directory: C:\Users\Steven\Documents\MyDocs

Checking for existing search indices...
✗ Chunk database not found
✗ File list not found
✗ File dictionary not found
✗ BM25 index not found
✗ ANN index not found

This will scan your documents and create search indexes.

--- MODE SELECTION ---

Choose your interface mode:

1. Simplified Mode
   - Quick setup with default settings
   - BM25 keyword search only
   - Returns 5 results per query
   - Best for: Quick searches and new users

2. Advanced Mode
   - Full control over all settings
   - Multiple search types (BM25, Direct/Regex, Semantic)
   - Customizable parameters
   - Best for: Power users and complex queries

Select mode (1-2): 2

✓ Advanced mode selected

--- Chunking Parameters ---
Chunk size: Number of words per text chunk (affects search granularity)
Chunk size [default: 256]: 256

Chunk overlap: Number of overlapping words between chunks (maintains context)
Chunk overlap [default: 16]: 16

--- Search Capabilities ---
Semantic search enables meaning-based search (slower but more intelligent)
Enable semantic search? (y/n) [default: y]: y

--- Configuration Summary ---
Directory: C:\Users\Steven\Documents\MyDocs
Chunk size: 256 words
Chunk overlap: 16 words
Semantic search: Enabled

Proceed with initialization? (y/n) [default: y]: y

----------------------------------------------------------------------
Initializing search engine... This may take a few minutes.
----------------------------------------------------------------------

[Progress bars and status messages...]

======================================================================
✓ Initialization complete!
✓ Indexed 150 files
✓ Created 3,421 text chunks
======================================================================
```

### Loading Existing Indices (Subsequent Runs)
```
======================================================================
                    SUPER SEARCH - Local Search Engine
======================================================================

--- MAIN MENU ---
Status: System not initialized

1. Initialize system
2. Exit

Select option (1-2): 1

--- SYSTEM INITIALIZATION ---

Current directory: C:\Users\Steven\Documents\MyDocs
Use current directory? (y/n) [default: y]: y

Selected directory: C:\Users\Steven\Documents\MyDocs

Checking for existing search indices...

Found existing search indices:
  ✓ Loaded chunk database: 3421 chunks
  ✓ Loaded file list: 150 files
  ✓ Loaded file dictionary
  ✓ Loaded BM25 index
  ✓ Loaded ANN index

Would you like to use these existing indices?
  - Yes: Skip scanning and use existing indices (faster)
  - No: Re-scan documents and rebuild all indices

Use existing indices? (y/n) [default: y]: y

--- MODE SELECTION ---

Choose your interface mode:

1. Simplified Mode
   - Quick setup with default settings
   - BM25 keyword search only
   - Returns 5 results per query
   - Best for: Quick searches and new users

2. Advanced Mode
   - Full control over all settings
   - Multiple search types (BM25, Direct/Regex, Semantic)
   - Customizable parameters
   - Best for: Power users and complex queries

Select mode (1-2): 2

✓ Advanced mode selected

======================================================================
✓ Successfully loaded existing indices!
✓ 150 files indexed
✓ 3421 text chunks
✓ BM25 keyword search available
✓ Semantic search available
======================================================================

--- MAIN MENU ---
Status: System initialized ✓ (Advanced Mode)

1. Perform search
2. Re-initialize system
3. Exit
```

### Continuing From Previous Session
```
======================================================================
                    SUPER SEARCH - Local Search Engine
======================================================================

--- MAIN MENU ---
Status: System not initialized

1. Initialize system
2. Exit

Select option (1-2): 1

--- SYSTEM INITIALIZATION ---

This will scan your documents and create search indexes.

Current directory: C:\Users\Steven\Documents\MyDocs
Use current directory? (y/n) [default: y]: y

--- Chunking Parameters ---
Chunk size: Number of words per text chunk (affects search granularity)
Chunk size [default: 256]: 256

Chunk overlap: Number of overlapping words between chunks (maintains context)
Chunk overlap [default: 16]: 16

--- Search Capabilities ---
Semantic search enables meaning-based search (slower but more intelligent)
Enable semantic search? (y/n) [default: y]: y

--- Configuration Summary ---
Directory: C:\Users\Steven\Documents\MyDocs
Chunk size: 256 words
Chunk overlap: 16 words
Semantic search: Enabled

Proceed with initialization? (y/n) [default: y]: y

----------------------------------------------------------------------
Initializing search engine... This may take a few minutes.
----------------------------------------------------------------------

[Progress bars and status messages...]

======================================================================
✓ Initialization complete!
✓ Indexed 150 files
✓ Created 3,421 text chunks
======================================================================

--- MAIN MENU ---
Status: System initialized ✓

1. Perform search
2. Re-initialize system
3. Exit

Select option (1-3): 1

--- SEARCH OPTIONS ---
1. BM25 Search (keyword-based, fast)
2. Direct Search (exact/regex matching)
3. Semantic Search (meaning-based, intelligent)
4. Return to main menu

Select search type (1-4): 3

Enter your search query: neural networks and deep learning

Number of results to return [default: 5]: 5

Query epsilon (lower = more accurate, slower) [0.01 - 1.0]
Epsilon [default: 0.1]: 0.1

Searching...

======================================================================
Results for: 'neural networks and deep learning' (Semantic Search (ANN))
======================================================================

--- Result 1 (Score: 0.3245) ---
File: C:\Users\Steven\Documents\MyDocs\research\ml_paper.pdf
Last modified: 2025-09-15 14:23:10
Chunk ID: 1245

Text preview:
Deep learning models, particularly convolutional neural networks (CNNs), 
have revolutionized computer vision tasks. These networks learn hierarchical 
representations of data through multiple layers of abstraction...

[More results...]

======================================================================
```

## Tips

1. **Verbose Mode for Debugging**: By default, the CLI runs in quiet mode with no debug logs. If you need to troubleshoot or see what's happening under the hood:
   ```bash
   python cli.py --verbose
   ```
   This shows logging from the search engine components and imported packages.

2. **Using Existing Indices**: On subsequent runs, always use existing indices if available. This is much faster than re-scanning. Only rebuild if:
   - You've added new documents to the directory
   - You want to change chunk size or overlap settings
   - You want to enable/disable semantic search

3. **First Time Setup**: Enable semantic search if you want the most intelligent results. You can always re-initialize later without it if it's too slow.

4. **Repeated Searches**: The CLI keeps all indexes in memory, so you can perform many searches quickly without re-initializing.

5. **Search Strategy**:
   - Use **BM25** when you know the exact terms
   - Use **Direct** for patterns or code
   - Use **Semantic** for concepts and ideas

6. **Performance**:
   - BM25: Fast (milliseconds)
   - Direct: Fast-Medium (depends on regex complexity)
   - Semantic: Medium (depends on epsilon and database size)

7. **Chunk Size Selection**:
   - Technical docs: 256-512 words
   - Research papers: 512-1024 words
   - Code files: 128-256 words
   - Books: 1024+ words

## Keyboard Shortcuts

- `Ctrl+C`: Exit the application at any time
- Just press `Enter`: Accept default values in prompts

## Troubleshooting

### "ModuleNotFoundError"
Make sure you've activated the virtual environment:
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### "No files found"
Check that:
- The directory path is correct
- The directory contains supported files (.pdf, .txt, .py, .md, etc.)
- You have read permissions for the directory

### "Initialization taking too long"
- Try disabling semantic search for faster initialization
- Check if there are very large files that need processing
- Consider using a smaller directory for testing

### Search returns no results
- Try broader search terms
- Check if the terms exist in your documents
- Try different search types (semantic vs keyword)
- Ensure initialization completed successfully

## Advanced Usage

### Regex Examples

Find email addresses:
```
Query: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
```

Find phone numbers:
```
Query: \(\d{3}\)\s*\d{3}-\d{4}
```

Find dates:
```
Query: \d{1,2}/\d{1,2}/\d{4}
```

### Epsilon Parameter Guide

For semantic search:
- `0.01-0.05`: Maximum accuracy, slower (research/academic)
- `0.1`: Good balance (default, recommended)
- `0.2-0.5`: Faster, still accurate (casual use)
- `0.5-1.0`: Very fast, less accurate (quick checks)

## Support

For issues or feature requests, visit: https://github.com/svanomm/super-search
