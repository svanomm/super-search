import json, re, os, sys
from typing import List, Dict, Union
from preprocess import preprocess

def query_direct(query: Union[str, re.Pattern]
                , chunk_db_path:str = None
                , chunks = None
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
    
    # If given a chunks db, don't load anything
    if chunks is None:
        if chunk_db_path is None:
            # Search for a default location index
            try:
                chunks = json.load(open("chunked_db.json", 'rb'))
            except Exception as e: 
                raise ValueError("Either chunk_db_path or chunks must be provided.")

        chunks = json.load(open(chunk_db_path, 'rb'))
    
    # Validate chunk database structure
    if 'processed_chunk' not in chunks or 'file_id' not in chunks:
        raise ValueError("Chunk database must contain 'processed_chunk' and 'file_id' keys.")

    # Prepare the search pattern
    if is_regex == True:
#        assert isinstance(query, re.Pattern), f"Invalid regular expression."
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags=flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}")
    else:
        # For simple string matching, escape special regex characters
        escaped_query = re.escape(preprocess(query))
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(escaped_query, flags=flags)
    
    # Search through chunks
    results = {'id': [], 'score': []}
    for idx, chunk_text in enumerate(chunks['processed_chunk']):
        # Find all matches in the chunk
        found_matches = pattern.findall(chunk_text)
        match_count = len(found_matches)
        if match_count > 0:
            # Calculate a relevance score based on match count
            results['id'].append(idx)
            results['score'].append(match_count)

    # Sort by score (descending) and id
    sorted_results = sorted(zip(results['id'], results['score']), key=lambda x: (-x[1], x[0]))

    # Limit to the top num_results
    sorted_results = sorted_results[:num_results]

    # normalize query scores to sum to 1
    scores = [r[1] for r in sorted_results]
    t=sum(scores)
    scores = [x / t for x in scores]

    # Format results to match the structure of other query functions
    results = {
        'id': [r[0] for r in sorted_results],
        'score': scores
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
