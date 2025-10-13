# In Progress
- interactive CLI
- multiprocess file ingestion

# Errors/Issues
- with small chunk sizes (e.g. 32), it's very likely that the top 10 results all come from the same file, which I'm assuming ppl may not want.
    - Need an ability to search at the file level for people to specify a number of files to return
    - BM25+keyword search seem best suited for this

# Want to Have
- **PERFORMANCE: Optimize query_direct() regex search - QUICK WINS COMPLETED ✓**
  
  ✓ COMPLETED Quick wins:
  - Replaced findall() with faster counting methods:
    * Non-regex: Uses str.lower().count() for case-insensitive (bypasses regex entirely)
    * Regex: Uses sum(1 for _ in pattern.finditer()) instead of findall()
  - Implemented heapq.nlargest() for efficient partial sorting (O(n log k) vs O(n log n))
  - Added optional multiprocessing for parallel chunk scanning on large databases (>1000 chunks)
    * Uses ProcessPoolExecutor for CPU-bound regex operations
    * Automatically disabled for small databases to avoid overhead
  
  REMAINING optimization opportunities:
  
  **Medium effort (significant speedup):**
  - Implement early termination with score threshold
  - Cache compiled regex patterns if same queries repeated
  - For simple keyword search, build a simple inverted index in memory on first load
  
  **Long-term (major refactor):**
  - Build lightweight inverted index for common keywords/n-grams (similar to BM25)
  - Use mmap for large chunk databases to reduce memory footprint
  - Consider using re2 library (Google's RE2) for faster regex matching (no backtracking)
  - Implement two-stage search: fast filter pass, then accurate scoring pass
  - For very large databases, consider pregexp or other optimized string search libraries
  
  **Benchmarking notes:**
  - Test with typical database size and query patterns
  - Compare against BM25 and NN search speeds to measure improvement
  - Profile with cProfile to confirm bottlenecks before implementing further optimizations

- Add an option for BM25 to look at file-level searches
- Add capability to chunk by sentence or by paragraph
    - Could make debugging a bit easier
- Return page number of a PDF chunk.
    - This is difficult because current chunking method first combines all text from the PDF into a single string, then breaks it up based on specified chunk length.
    - would need to extract into a dict of page_text and page_num, preprocess each page separately, then perform "page-aware chunking" so that the chunk DB stores the minimum page number for each chunk
    - Easier method would just use 1 chunk per page for PDFs, no overlap
        - Weakness is for paragraphs that span pages
        - Other weakness is that semantic search could be less meaningful with that many tokens
- Return the original text without processing
    - would need to save both the original text and the processed text, which doubles the chunk db size
    - original text is not necessarily the cleanest 
- chunk_db needs to be able to update an existing database

# Future Plans
- Incorporate a reranker model to order results from multiple search types
- Search logic: small queries should prioritize exact match search over semantic search
    - More generally, we should decide the best search method based on the query
    - Found that single words are faster to search in BM25 in current implementation (because of BM25 index)