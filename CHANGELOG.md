# Changelog

## Latest Updates - October 2025

### Added Verbose Mode for Logging Control

The CLI now suppresses all debug logging by default for a clean user experience.

#### 🎯 Key Features
- **Clean Default Output**: No debug logs, warnings, or info messages clutter the interface by default
- **Optional Verbose Mode**: Enable logging when needed for debugging with `--verbose` or `-v` flag
- **Suppressed Third-Party Logs**: Automatically suppresses noisy logs from imported packages (JAX, BM25s, Model2Vec, etc.)
- **Better UX**: Users see only the interface and their results, not internal operations

#### 💡 Usage

**Normal mode (clean output):**
```bash
python cli.py
```

**Verbose mode (with logging):**
```bash
python cli.py --verbose
# or
python cli.py -v
```

#### 🔧 Technical Implementation

**File: cli.py**
- Added argument parsing with `argparse` for `--verbose` flag
- Added `setup_logging()` function to configure logging levels
- Logs configured early before imports to suppress package initialization logs
- Suppresses loggers from: jax, bm25s, model2vec, pynndescent, pymupdf, tqdm
- Environment variable `TF_CPP_MIN_LOG_LEVEL` set to suppress TensorFlow logs

**File: CLI_GUIDE.md**
- Updated Quick Start section with verbose flag examples
- Added tip about using verbose mode for debugging

### Improved Initialization Flow

The initialization process has been redesigned for a better user experience.

#### 🔄 New Initialization Flow
1. **Directory Selection First**: Users now select their document directory before any other steps
2. **Check for Existing Indices**: System checks the selected directory for existing indices
3. **Mode Selection**: Users choose Simplified or Advanced mode only when needed (not at startup)
4. **Contextual Configuration**: Settings are collected based on the chosen mode

#### 🎯 Key Benefits
- **More Intuitive**: Directory selection happens first, making the workflow more logical
- **Faster for Existing Indices**: Mode selection deferred until after checking for existing indices
- **Better Context**: Users see what's available before choosing how to proceed
- **Flexible**: Can still rebuild indices in any directory at any time

#### 💡 Updated User Flow

**First Run (No existing indices):**
```
1. Start CLI
2. Choose "Initialize system"
3. Select directory
4. System checks for indices (none found)
5. Choose mode (Simplified/Advanced)
6. Configure settings based on mode
7. Initialize and start searching
```

**Subsequent Runs (Existing indices found):**
```
1. Start CLI
2. Choose "Initialize system"
3. Select directory (same as before)
4. System finds existing indices
5. Choose to use existing or rebuild
6. If using existing: Choose mode → Ready to search
7. If rebuilding: Choose mode → Configure → Initialize
```

#### 🔧 Technical Changes

**File: cli.py**
- Moved mode selection from `run()` to `initialize_system()`
- Directory selection now happens first in initialization flow
- Mode selection happens after checking for existing indices
- Updated logic to handle mode selection contextually

**File: CLI_GUIDE.md**
- Updated all examples to reflect new flow
- Revised quick start instructions
- Updated workflow descriptions

### Added Load Existing Indices Feature

Users can now quickly reload previously created search indices instead of re-scanning all documents.

#### 🎯 Key Benefits
- **Much Faster Startup**: Skip document scanning and index building when indices already exist
- **Smart Detection**: Automatically checks for existing chunk database, BM25 index, and ANN index
- **Flexible Loading**: Can proceed even if some indices are missing (with limited functionality)
- **Clear Feedback**: Shows which indices are available and which are missing
- **User Choice**: Always asks before using existing indices vs. rebuilding

#### 📍 Expected Index Locations
- Chunk database: `./search_utils/chunked_db.json`
- File list: `./search_utils/file_list.json`
- File dictionary: `./search_utils/file_dict.json`
- BM25 index: `./search_utils/index_bm25/`
- ANN index: `./search_utils/nn_database.pkl`

#### 🔧 Technical Implementation

**File: src/initialize.py**
- Added `load_existing_indices()` function to check and load existing indices
- Scans expected locations for all index files
- Attempts to load each found index
- Returns detailed status with success flags and messages
- Handles partial index availability gracefully

**File: cli.py**
- Updated `initialize_system()` to check for existing indices after directory selection
- Prompts user to choose between using existing indices or rebuilding
- Validates that minimum required components (chunk database, file list) are present
- Displays clear status of what's available and what's missing
- Falls back to full initialization if indices are incomplete or user chooses to rebuild

#### 💡 User Experience

When initializing:
```
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

Use existing indices? (y/n) [default: y]:
```

#### 🔄 When to Rebuild Indices
- Added new documents to the directory
- Changed chunk size or overlap settings
- Want to enable/disable semantic search
- Indices are corrupted or incomplete

### Added Clickable File Hyperlinks

**File: cli.py**
- Updated `display_results()` to convert file paths to clickable hyperlinks
- Uses ANSI OSC 8 escape sequences for terminal hyperlink support
- Converts paths to absolute paths and file:// URIs
- Works in modern Windows terminals (Windows Terminal, PowerShell)

#### Example Output
Results now display file paths as clickable links that open the file when clicked.

---

## CLI Updates - October 2025

### Added Mode Selection Feature

The interactive CLI now supports two distinct modes of operation:

#### 🚀 Simplified Mode
- **Purpose**: Quick searches for new users and common use cases
- **Features**:
  - Zero configuration - uses sensible defaults
  - Automatic directory selection (current working directory)
  - Fixed chunk size: 256 words
  - Fixed chunk overlap: 16 words
  - BM25 keyword search only (fastest initialization)
  - Fixed 5 results per query
  - No semantic search (faster setup)
  - Type "back" to return to main menu while searching
  
- **When to use**:
  - First time using the tool
  - Quick document searches
  - Finding specific terms or phrases
  - When speed matters more than customization

#### ⚙️ Advanced Mode
- **Purpose**: Full control for power users and complex queries
- **Features**:
  - Custom directory selection
  - Adjustable chunk size and overlap
  - Multiple search types: BM25, Direct/Regex, Semantic
  - Optional semantic search indexing
  - Customizable number of results
  - Search-specific options (case sensitivity, regex, epsilon)
  
- **When to use**:
  - Need fine-tuned control over parameters
  - Using regex or semantic search
  - Working with specific document types
  - Optimizing for performance or accuracy

### Technical Changes

**File: cli.py**
- Added `mode` attribute to `SearchCLI` class
- Added `select_mode()` method for mode selection at startup
- Modified `initialize_system()` to use defaults in simplified mode
- Modified `search_menu()` to provide streamlined interface in simplified mode
- Updated `main_menu()` to display current mode
- Updated `run()` to call mode selection before main menu

**File: CLI_GUIDE.md**
- Added mode comparison table
- Added simplified mode workflow section
- Added simplified mode examples
- Reorganized content for clarity

### User Experience Improvements

1. **Clear Mode Selection**: Users immediately choose their experience level
2. **Visual Indicators**: Mode is displayed in the main menu status line
3. **Consistent Experience**: Mode choice persists throughout the session
4. **Easy Exit**: Simplified mode allows typing "back" to exit search
5. **No Prompts**: Simplified mode eliminates all configuration prompts

### Migration Notes

- Existing users can continue using Advanced Mode (option 2)
- New users should start with Simplified Mode (option 1)
- Mode selection happens once at startup
- Re-initialization maintains the chosen mode

### Example Usage

**Simplified Mode:**
```bash
python cli.py
Select mode (1-2): 1
# Uses all defaults, BM25 search only, 5 results
```

**Advanced Mode:**
```bash
python cli.py
Select mode (1-2): 2
# Full customization as before
```
