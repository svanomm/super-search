#!/usr/bin/env python3
"""
Interactive Command Line Interface for Super Search
A local document search engine with keyword and semantic search capabilities.
"""

import os
import sys
import logging
import argparse
import warnings
from pathlib import Path

# Suppress all logging and warnings early, before imports
# This will be reconfigured later based on command-line arguments
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs if present
logging.basicConfig(level=logging.CRITICAL)
warnings.filterwarnings('ignore')

# Suppress specific loggers before importing packages
for logger_name in ['jax', 'jax._src', 'jaxlib', 'absl', 'bm25s', 'model2vec', 'pynndescent', 'pymupdf', 'tqdm']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).propagate = False

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from utils import convert_results
from queries import query_bm25, query_direct, query_nn
from initialize import initialize, load_existing_indices


def setup_logging(verbose=False):
    """
    Configure logging levels for the application.
    
    Args:
        verbose: If True, show all logging output. If False, suppress all logs.
    """
    if verbose:
        # Show all logs at INFO level and above
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s',
            force=True
        )
        # Re-enable third-party package logging
        for logger_name in ['bm25s', 'model2vec', 'pynndescent', 'pymupdf', 'tqdm']:
            logging.getLogger(logger_name).setLevel(logging.INFO)
            logging.getLogger(logger_name).propagate = True
        
        # Keep JAX quiet even in verbose mode (too noisy)
        for logger_name in ['jax', 'jax._src', 'jaxlib', 'absl']:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    else:
        # Suppress all logs except CRITICAL (already configured above)
        logging.basicConfig(
            level=logging.CRITICAL,
            format='%(levelname)s: %(message)s',
            force=True
        )


class SearchCLI:
    """Interactive command line interface for the search engine."""
    
    def __init__(self):
        self.files = None
        self.file_dict = None
        self.chunks = None
        self.bm25_retriever = None
        self.ann_index = None
        self.initialized = False
        self.has_semantic = False
        self.mode = None  # 'simplified' or 'advanced'
        
    def print_banner(self):
        """Print welcome banner."""
        print("\n" + "="*70)
        print(" "*20 + "SUPER SEARCH - Local Search Engine")
        print("="*70 + "\n")
    
    def select_mode(self):
        """Allow user to select simplified or advanced mode."""
        print("--- MODE SELECTION ---\n")
        print("Choose your interface mode:\n")
        print("1. Simplified Mode")
        print("   - Quick setup with default settings")
        print("   - BM25 keyword search only")
        print("   - Returns 5 results per query")
        print("   - Best for: Quick searches and new users\n")
        print("2. Advanced Mode")
        print("   - Full control over all settings")
        print("   - Multiple search types (BM25, Direct/Regex, Semantic)")
        print("   - Customizable parameters")
        print("   - Best for: Power users and complex queries\n")
        
        while True:
            choice = input("Select mode (1-2): ").strip()
            if choice == '1':
                self.mode = 'simplified'
                print("\n✓ Simplified mode selected\n")
                return
            elif choice == '2':
                self.mode = 'advanced'
                print("\n✓ Advanced mode selected\n")
                return
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    def get_user_input(self, prompt, default=None, input_type=str, validator=None):
        """
        Get validated user input.
        
        Args:
            prompt: The prompt to display
            default: Default value if user presses enter
            input_type: Type to convert input to
            validator: Optional function to validate input
        """
        while True:
            if default is not None:
                user_input = input(f"{prompt} [default: {default}]: ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()
                if not user_input:
                    print("Input cannot be empty. Please try again.")
                    continue
            
            try:
                value = input_type(user_input)
                if validator and not validator(value):
                    print("Invalid input. Please try again.")
                    continue
                return value
            except ValueError:
                print(f"Invalid input type. Expected {input_type.__name__}.")
    
    def initialize_system(self):
        """Guide user through initialization process."""
        print("\n--- SYSTEM INITIALIZATION ---\n")
        
        # Step 1: Get directory path first
        default_path = os.getcwd()
        path = self.get_user_input("Enter path to document directory, or press enter to use", default=default_path)
        
        # Step 2: Check for existing indices in the selected directory
        print("\nChecking for existing search indices...")
        existing = load_existing_indices(path)
        
        use_existing = False
        if existing['success'] and existing['has_chunks']:
            # Display what was found
            print("\nFound existing search indices:")
            for msg in existing['messages']:
                print(f"  {msg}")
            
            print("\nWould you like to use these existing indices?")
            print("  - Yes: Skip scanning and use existing indices (faster)")
            print("  - No: Re-scan documents and rebuild all indices")
            
            choice = input("\nUse existing indices? (y/n) [default: y]: ").strip().lower()
            use_existing = choice not in ['n', 'no']
            
            if use_existing:
                # Validate that we have the minimum required components
                if not existing['has_chunks']:
                    print("\n✗ Cannot proceed: Chunk database is required but not found.")
                    print("Will need to re-initialize from scratch.\n")
                    use_existing = False
                elif not existing['files'] or not existing['file_dict']:
                    print("\n✗ Warning: File list or file dictionary missing.")
                    print("Will need to re-initialize from scratch.\n")
                    use_existing = False
                else:
                    # Step 3: Ask for mode selection before loading
                    if self.mode is None:
                        self.select_mode()
                    
                    # Load the existing data
                    self.chunks = existing['chunks']
                    self.files = existing['files']
                    self.file_dict = existing['file_dict']
                    self.bm25_retriever = existing['bm25_retriever']
                    self.ann_index = existing['ann_index']
                    self.has_semantic = existing['has_ann']
                    
                    # Check what's missing and inform user
                    missing = []
                    if not existing['has_bm25']:
                        missing.append("BM25 index")
                    if not existing['has_ann']:
                        missing.append("ANN index")
                    
                    if missing:
                        print(f"\n⚠ Warning: Some indices are missing: {', '.join(missing)}")
                        print("You can still search using available methods.")
                        if not self.bm25_retriever and self.mode == 'simplified':
                            print("\n✗ Simplified mode requires BM25 index.")
                            print("Please rebuild indices or use advanced mode.\n")
                            return False
                    
                    self.initialized = True
                    print("\n" + "="*70)
                    print("✓ Successfully loaded existing indices!")
                    print(f"✓ {len(self.files['filepath'])} files indexed")
                    print(f"✓ {len(self.chunks['processed_chunk'])} text chunks")
                    if existing['has_bm25']:
                        print("✓ BM25 keyword search available")
                    if existing['has_ann']:
                        print("✓ Semantic search available")
                    print("="*70 + "\n")
                    return True
        
        # Step 3: If not using existing indices, ask for mode selection
        if not use_existing:
            print("\nThis will scan your documents and create search indexes.")
            
            if self.mode is None:
                self.select_mode()
        
        # Step 4: Get initialization parameters based on mode
        # Simplified mode uses defaults without prompting
        if self.mode == 'simplified':
            chunk_size = 256
            chunk_overlap = 16
            semantic_search = False  # Simplified mode only uses BM25
            
            print(f"\nUsing directory: {path}")
            print("Using default settings:")
            print(f"  - Chunk size: {chunk_size} words")
            print(f"  - Chunk overlap: {chunk_overlap} words")
            print(f"  - Search type: BM25 keyword search only")
            
            confirm = input("\nProceed with initialization? (y/n) [default: y]: ").strip().lower()
            if confirm in ['n', 'no']:
                print("Initialization cancelled.")
                return False
        
        # Advanced mode prompts for all options
        else:
            # Get chunking parameters
            print("\n--- Chunking Parameters ---")
            print("Chunk size: Number of words per text chunk (affects search granularity)")
            chunk_size = self.get_user_input(
                "Chunk size", 
                default=256, 
                input_type=int,
                validator=lambda x: x > 0
            )
            
            print("Chunk overlap: Number of overlapping words between chunks (maintains context)")
            chunk_overlap = self.get_user_input(
                "Chunk overlap", 
                default=16, 
                input_type=int,
                validator=lambda x: x >= 0
            )
            
            # Ask about semantic search
            print("\n--- Search Capabilities ---")
            print("Semantic search enables meaning-based search (slower but more intelligent)")
            semantic_choice = input("Enable semantic search? (y/n) [default: y]: ").strip().lower()
            semantic_search = semantic_choice not in ['n', 'no']
            
            # Confirm before proceeding
            print("\n--- Configuration Summary ---")
            print(f"Directory: {path}")
            print(f"Chunk size: {chunk_size} words")
            print(f"Chunk overlap: {chunk_overlap} words")
            print(f"Semantic search: {'Enabled' if semantic_search else 'Disabled'}")
            
            confirm = input("\nProceed with initialization? (y/n) [default: y]: ").strip().lower()
            if confirm in ['n', 'no']:
                print("Initialization cancelled.")
                return False
        
        # Step 5: Initialize the system
        print("\n" + "-"*70)
        print("Initializing search engine... This may take a few minutes.")
        print("-"*70 + "\n")
        
        try:
            return_packet = initialize(
                path=path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                semantic_search=semantic_search
            )
            
            # Store the components
            self.files = return_packet['files']
            self.file_dict = return_packet['file_dict']
            self.chunks = return_packet['chunks']
            self.bm25_retriever = return_packet['bm25_retriever']
            self.has_semantic = semantic_search
            
            if semantic_search and 'ann_index' in return_packet:
                self.ann_index = return_packet['ann_index']
            
            self.initialized = True
            
            print("\n" + "="*70)
            print("✓ Initialization complete!")
            print(f"✓ Indexed {len(self.files['filepath'])} files")
            print(f"✓ Created {len(self.chunks['processed_chunk'])} text chunks")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error during initialization: {e}")
            return False
    
    def display_results(self, results_full, query_text, search_type):
        """Display search results in a readable format."""
        print("\n" + "="*70)
        print(f"Results for: '{query_text}' ({search_type})")
        print("="*70)
        
        if not results_full['chunk_id']:
            print("\nNo results found.")
            return
        
        for idx, chunk_id in enumerate(results_full['chunk_id'], 1):
            score = results_full['score'][idx-1]
            chunk_text = results_full['processed_chunk'][idx-1]
            file_props = results_full['file_properties'][idx-1]
            
            # Convert file path to absolute path and create clickable hyperlink
            filepath = os.path.abspath(file_props['filepath'])
            file_uri = Path(filepath).as_uri()
            hyperlink = f"\x1b]8;;{file_uri}\x1b\\{filepath}\x1b]8;;\x1b\\"
            
            print(f"\n--- Result {idx} (Score: {score:.4f}) ---")
            print(f"File: {hyperlink}")
            print(f"Last modified: {file_props['last_modified']}")
            print(f"Chunk ID: {chunk_id}")
            print(f"\nText preview:")
            # Show first 300 characters
            preview = chunk_text[:300] + "..." if len(chunk_text) > 300 else chunk_text
            print(preview)
        
        print("\n" + "="*70)
    
    def search_menu(self):
        """Display search options and handle search queries."""
        # Simplified mode: streamlined search with no options
        if self.mode == 'simplified':
            while True:
                print("\n--- SEARCH ---")
                print("Using: BM25 keyword search, 5 results")
                print("\nEnter 'back' to return to main menu")
                
                query_text = input("\nEnter your search query: ").strip()
                
                if query_text.lower() == 'back':
                    break
                
                if not query_text:
                    print("Query cannot be empty.")
                    continue
                
                # Perform search with defaults
                try:
                    print("\nSearching...")
                    
                    results = query_bm25(
                        query=query_text,
                        retriever=self.bm25_retriever,
                        num_results=5
                    )
                    
                    # Convert results to include full information
                    results_full = convert_results(results, self.chunks, self.file_dict)
                    
                    # Display results
                    self.display_results(results_full, query_text, "BM25 Keyword Search")
                    
                except Exception as e:
                    print(f"\n✗ Error during search: {e}")
        
        # Advanced mode: full menu with all options
        else:
            while True:
                print("\n--- SEARCH OPTIONS ---")
                print("1. BM25 Search (keyword-based, fast)")
                print("2. Direct Search (exact/regex matching)")
                if self.has_semantic:
                    print("3. Semantic Search (meaning-based, intelligent)")
                print("4. Return to main menu")
                
                choice = input("\nSelect search type (1-4): ").strip()
                
                if choice == '4':
                    break
                
                if choice not in ['1', '2', '3']:
                    print("Invalid choice. Please try again.")
                    continue
                
                if choice == '3' and not self.has_semantic:
                    print("Semantic search not available. Please choose another option.")
                    continue
                
                # Get search query
                query_text = input("\nEnter your search query: ").strip()
                if not query_text:
                    print("Query cannot be empty.")
                    continue
                
                # Get number of results
                num_results = self.get_user_input(
                    "Number of results to return",
                    default=5,
                    input_type=int,
                    validator=lambda x: x > 0
                )
                
                # Perform search
                try:
                    print("\nSearching...")
                    
                    if choice == '1':
                        results = query_bm25(
                            query=query_text,
                            retriever=self.bm25_retriever,
                            num_results=num_results
                        )
                        search_type = "BM25 Keyword Search"
                    
                    elif choice == '2':
                        # Ask about case sensitivity
                        case_sens = input("Case sensitive? (y/n) [default: n]: ").strip().lower()
                        case_sensitive = case_sens in ['y', 'yes']
                        
                        # Ask about regex
                        use_regex = input("Use regex? (y/n) [default: n]: ").strip().lower()
                        is_regex = use_regex in ['y', 'yes']
                        
                        results = query_direct(
                            query=query_text,
                            chunks=self.chunks,
                            num_results=num_results,
                            case_sensitive=case_sensitive,
                            is_regex=is_regex
                        )
                        search_type = f"Direct Search ({'regex' if is_regex else 'exact'}, {'case-sensitive' if case_sensitive else 'case-insensitive'})"
                    
                    elif choice == '3':
                        # Ask about epsilon for ANN
                        print("Query epsilon (lower = more accurate, slower) [0.01 - 1.0]")
                        epsilon = self.get_user_input(
                            "Epsilon",
                            default=0.1,
                            input_type=float,
                            validator=lambda x: 0.01 <= x <= 1.0
                        )
                        
                        results = query_nn(
                            query=query_text,
                            index=self.ann_index,
                            num_results=num_results,
                            query_epsilon=epsilon
                        )
                        search_type = "Semantic Search (ANN)"
                    
                    # Convert results to include full information
                    results_full = convert_results(results, self.chunks, self.file_dict)
                    
                    # Display results
                    self.display_results(results_full, query_text, search_type)
                    
                except Exception as e:
                    print(f"\n✗ Error during search: {e}")
    
    def main_menu(self):
        """Display main menu and handle user choices."""
        while True:
            print("\n--- MAIN MENU ---")
            mode_display = f" ({self.mode.title()} Mode)" if self.mode else ""
            if self.initialized:
                print(f"Status: System initialized ✓{mode_display}")
                print("\n1. Perform search")
                print("2. Re-initialize system")
                print("3. Exit")
                
                choice = input("\nSelect option (1-3): ").strip()
                
                if choice == '1':
                    self.search_menu()
                elif choice == '2':
                    confirm = input("This will re-scan documents. Continue? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        self.initialize_system()
                elif choice == '3':
                    print("\nThank you for using Super Search!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            else:
                print(f"Status: System not initialized{mode_display}")
                print("\n1. Initialize system")
                print("2. Exit")
                
                choice = input("\nSelect option (1-2): ").strip()
                
                if choice == '1':
                    self.initialize_system()
                elif choice == '2':
                    print("\nGoodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
    
    def run(self):
        """Main entry point for the CLI application."""
        try:
            self.print_banner()
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
        except Exception as e:
            print(f"\n\nUnexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Entry point for the CLI application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Super Search - Local document search engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py              Run with default settings (no logging)
  python cli.py --verbose    Run with verbose logging output
  python cli.py -v           Run with verbose logging output (short form)
        """
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging output for debugging'
    )
    
    args = parser.parse_args()
    
    # Set up logging based on verbose flag
    setup_logging(verbose=args.verbose)
    
    # Run the CLI
    cli = SearchCLI()
    cli.run()


if __name__ == "__main__":
    main()
