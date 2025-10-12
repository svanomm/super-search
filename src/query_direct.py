import json, re, os, sys
from typing import List, Dict, Union

def query_direct(query: Union[str, re.Pattern]
                , chunk_db_path: str = None
                , num_results: int = 3
                , case_sensitive: bool = False
                , is_regex: bool = False
                ):
    """
    Search through text chunks using direct keyword matching or regular expressions.

    Args:
        query (str or re.Pattern): Search query string or compiled regex pattern.
        chunk_db_path (str, optional): Path to the chunked database JSON file.
        num_results (int, optional): Maximum number of results to return. Defaults to 3.
        case_sensitive (bool, optional): Whether search should be case-sensitive. Defaults to False.
        is_regex (bool, optional): Whether to treat query as a regular expression. Defaults to False.

    Returns:
        dict: A dictionary with keys 'id', 'score', 'chunk_text', and 'filepath',
              each containing a list of results.
    """
    
    ### Error checks
    num_results = 1 if num_results < 1 else num_results
    
    # Load the chunk database
    if chunk_db_path is None:
        # Search for default location
        default_paths = [
            "chunked_db.json",
            "../chunked_db.json",
            "src/chunked_db.json"
        ]
        
        chunk_db_path = None
        for path in default_paths:
            if os.path.exists(path):
                chunk_db_path = path
                break
        
        if chunk_db_path is None:
            raise ValueError("chunk_db_path must be provided or a default chunked_db.json must exist.")
    
    # Load the database
    try:
        with open(chunk_db_path, 'r', encoding='utf-8') as f:
            chunk_db = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Chunk database not found at: {chunk_db_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in chunk database: {chunk_db_path}")
    
    # Validate chunk database structure
    if 'processed_chunk' not in chunk_db or 'file_path' not in chunk_db:
        raise ValueError("Chunk database must contain 'processed_chunk' and 'file_path' keys.")
    
    # Prepare the search pattern
    if isinstance(query, re.Pattern):
        pattern = query
        is_regex = True
    elif is_regex:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags=flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}")
    else:
        # For simple string matching, escape special regex characters
        escaped_query = re.escape(query)
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(escaped_query, flags=flags)
    
    # Search through chunks
    matches = []
    for idx, chunk_text in enumerate(chunk_db['processed_chunk']):
        # Find all matches in the chunk
        found_matches = pattern.finditer(chunk_text)
        match_count = 0
        match_positions = []
        
        for match in found_matches:
            match_count += 1
            match_positions.append(match.start())
        
        if match_count > 0:
            # Calculate a relevance score based on match count and early position
            # Higher score for more matches and earlier positions
            avg_position = sum(match_positions) / len(match_positions) if match_positions else len(chunk_text)
            position_score = 1 / (1 + avg_position / len(chunk_text))
            score = match_count * 10 + position_score
            
            matches.append({
                'id': idx,
                'score': score,
                'match_count': match_count,
                'chunk_text': chunk_text,
                'filepath': chunk_db['file_path'][idx]
            })
    
    # Sort by score (descending) and limit results
    matches.sort(key=lambda x: x['score'], reverse=True)
    matches = matches[:num_results]
    
    # Format results to match the structure of other query functions
    results = {
        'id': [m['id'] for m in matches],
        'score': [m['score'] for m in matches],
        'match_count': [m['match_count'] for m in matches],
        'chunk_text': [m['chunk_text'] for m in matches],
        'filepath': [m['filepath'] for m in matches]
    }
    
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Query chunk database using direct keyword or regex search")
    parser.add_argument("query", nargs='?', help="Search query string or regular expression")
    parser.add_argument("--chunk_db_path", "-d", help="Path to chunk database JSON file", default="chunked_db.json")
    parser.add_argument("--num_results", "-n", type=int, default=3, help="Maximum number of results to return")
    parser.add_argument("--case_sensitive", "-c", action="store_true", help="Enable case-sensitive search")
    parser.add_argument("--regex", "-r", action="store_true", help="Treat query as a regular expression")

    # If run with no arguments or explicitly asking for help using --help or --h, display documentation and options
    if len(sys.argv) == 1 or "--help" in sys.argv or "--h" in sys.argv:
        if query_direct.__doc__:
            print(query_direct.__doc__)
        print("\nUsage and options:")
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    try:
        results = query_direct(
            args.query,
            chunk_db_path=args.chunk_db_path,
            num_results=args.num_results,
            case_sensitive=args.case_sensitive,
            is_regex=args.regex
        )
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    print(json.dumps(results, indent=2))
