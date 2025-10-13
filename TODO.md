# In Progress
- 

# Errors/Issues
- with small chunk sizes (e.g. 32), it's very likely that the top 10 results all come from the same file, which I'm assuming ppl may not want.
    - Need an ability to search at the file level for people to specify a number of files to return
    - BM25+keyword search seem best suited for this

# Want to Have
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

# Future Plans
- Incorporate a reranker model to order results from multiple search types
- Search logic: small queries should prioritize exact match search over semantic search
    - More generally, we should decide the best search method based on the query
    - Found that single words are faster to search in BM25 in current implementation (because of BM25 index)