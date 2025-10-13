def convert_results(results, chunks, file_dict):
    """
    Convert search results results to include full chunk and file properties.
    Args:
        results (dict): The BM25 results with 'id' and 'score'.
        chunks (dict): The chunks data with 'processed_chunk', 'chunk_id', and 'file_id'.
        file_dict (dict): A dictionary mapping file_id to file properties.
    Returns:
        dict: A dictionary with full chunk and file properties.
    """
    results_full = {
        'processed_chunk': [chunks['processed_chunk'][i] for i in results['id']],
        'score': results['score'],
        'chunk_id': [chunks['chunk_id'][i] for i in results['id']],
        'file_id': [chunks['file_id'][i] for i in results['id']]
    }

    results_full['file_properties'] = [file_dict[i] for i in results_full['file_id']]

    return results_full