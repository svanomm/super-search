import os
import logging
from datetime import datetime
from file_scanner import file_scanner
from chunk_db import chunk_db
from create_bm25_index import create_bm25_index
from query_bm25 import query_bm25
from gui_frontend import make_window
import FreeSimpleGUI as sg
from math import floor

def setup_logging():
    """Set up logging with timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"search_log_{timestamp}.txt"
    log_path = os.path.join(os.path.dirname(__file__), log_filename)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also log to console
        ]
    )
    return logging.getLogger(__name__)

def log_print(message):
    """Custom print function that logs to both file and console"""
    logger.info(message)

def main():
    global logger
    logger = setup_logging()
    log_print("Application started")
    
    window = make_window(sg.theme())
    
    # Initialize global variables
    index_directory = ''
    index_location = ''
    file_list_display = ''
    file_list = []
    flag_semantic_index = 0
    search_results = []
    bm25_index_path = 'index_bm25'  # Default BM25 index path
    num_files_to_chunk = 0

    
    # Check if index already exists and update status
    if os.path.exists(bm25_index_path):
        window['-INDEX STATUS-'].update(f"Index found: {bm25_index_path}")
        log_print(f"Found existing BM25 index at: {bm25_index_path}")
    else:
        window['-INDEX STATUS-'].update("No index found - build an index first")
        log_print("No existing BM25 index found")

    # This is an Event Loop 
    while True:
        event, values = window.read(timeout=100)
        # keep an animation running so show things are happening
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            log_print('============ Event = ' + str(event) + ' ==============')
            log_print('-------- Values Dictionary (key=value) --------')
            for key in values:
                log_print(str(key) + ' = ' + str(values[key]))
        if event in (None, 'Exit'):
            log_print("[LOG] Clicked Exit!")
            break
        if event == 'About':
            sg.popup('PySimpleGUI Demo All Elements',
                        'Right click anywhere to see right click menu',
                        'Visit each of the tabs to see available elements',
                        'Output of event and values can be see in Output tab',
                        'The event and values dictionary is printed after every event', keep_on_top=True)
        elif event == 'Popup':
            sg.popup("You pressed a button!", keep_on_top=True)
        elif event == 'Test Progress bar':
            progress_bar = window['-PROGRESS BAR-']
            for i in range(100):
                progress_bar.update(current_count=i + 1)

        elif event == "Open Folder to Index":
            files = sg.popup_get_folder('Choose your folder', keep_on_top=True)
            if files:
                window['-INDEX DIRECTORY-'].update(files)
                index_directory = files

                # Run file scanner on the folder
                file_list = file_scanner(files, allowed_text_types=['pdf'])
                num_files_to_chunk = len(file_list['filepath'])
                file_list_display = '\n'.join(file_list['filepath']) if file_list else 'No files found.'
                window['-FILELIST_DISPLAY-'].update(file_list_display)

        elif event == "Open Index":
            folder_or_file = sg.popup_get_file('Choose your file', keep_on_top=True)
            sg.popup("You chose: " + str(folder_or_file), keep_on_top=True)

        elif event == 'Create semantic index in addition to BM25':
            flag_semantic_index = 1

        elif event == '-BUILD_INDEX-':
            if not file_list:
                sg.popup_error("No files to index. Please select a folder to index first.", keep_on_top=True)
            else:
                try:
                    log_print("Starting index building process...")

                    def gui_progress_callback(current: int) -> int:
                        sg.one_line_progress_meter(
                            "Building chunk database", 
                            current, 
                            num_files_to_chunk, 
                            key='-CHUNK_PROGRESS_BAR-', 
                            orientation='h', 
                            keep_on_top=True
                        )
                    
                    db, _ = chunk_db(file_list=file_list, chunk_size=99999999, progress_callback=gui_progress_callback)
                    
                    # Close the progress meter window when done
                    sg.one_line_progress_meter_cancel(key='-CHUNK_PROGRESS_BAR-')
                    
                    log_print("Chunk database created successfully. Creating BM25 index...")
                    sg.popup("Creating BM25 index...", keep_on_top=True, auto_close=True, auto_close_duration=2)
                    retriever = create_bm25_index(chunk_db_path='../chunked_db.json')
                    
                    # Update the BM25 index path - the index is saved as 'index_bm25' directory
                    bm25_index_path = 'index_bm25'
                    log_print(f"BM25 index saved to: {bm25_index_path}")
                    
                    # Update index status in GUI
                    try:
                        # Try to load the index to get document count
                        # This would normally use: retriever = bm25s.BM25.load(bm25_index_path, load_corpus=True)
                        # For now, we'll show a general status
                        index_status = f"Index ready: {bm25_index_path}"
                        window['-INDEX STATUS-'].update(index_status)
                    except Exception:
                        window['-INDEX STATUS-'].update("Index built (status unknown)")
                    
                    sg.popup("Index built successfully! You can now search your documents.", keep_on_top=True, auto_close=True, auto_close_duration=3)
                    
                except Exception as e:
                    error_msg = f"Error building index: {str(e)}"
                    sg.popup_error(error_msg, keep_on_top=True)
                    log_print(error_msg)

        elif event == 'Search':
            query = values['-SEARCH QUERY-']
            if not query.strip():
                sg.popup_error("Please enter a search query.", keep_on_top=True)
            elif not os.path.exists(bm25_index_path):
                sg.popup_error("No BM25 index found. Please build an index first.", keep_on_top=True)
            else:
                try:
                    log_print(f"Searching for: '{query}'")
                    # Perform BM25 search
                    results = query_bm25(query=query, index_path=bm25_index_path, num_results=10)
                    
                    # Format results for display
                    search_results = []
                    if results['text'] and len(results['text']) > 0:
                        for i, (text, chunk_id) in enumerate(zip(results['text'], results['id'])):
                            # Clean up text for display - remove extra whitespace and newlines
                            clean_text = ' '.join(text.split())
                            # Truncate text for display in listbox
                            display_text = clean_text[:150] + "..." if len(clean_text) > 150 else clean_text
                            search_results.append(f"[{i+1}]: {display_text}")
                        
                        # Update the search results listbox
                        window['-SEARCH RESULTS-'].update(search_results)
                        log_print(f"Found {len(search_results)} results for query: '{query}'")
                    else:
                        # No results found
                        window['-SEARCH RESULTS-'].update(["No results found for your query."])
                        log_print(f"No results found for query: '{query}'")
                    
                except Exception as e:
                    error_msg = f"Error performing search: {str(e)}"
                    sg.popup_error(error_msg, keep_on_top=True)
                    log_print(error_msg)
                    # Clear results on error
                    window['-SEARCH RESULTS-'].update([f"Error: {str(e)}"])

        elif event == 'Clear Search':
            window['-SEARCH QUERY-'].update('')
            window['-SEARCH RESULTS-'].update([])
            search_results = []

        elif event == '-SEARCH QUERY-':
            # Handle Enter key press in search query field
            if '\r' in values['-SEARCH QUERY-'] or '\n' in values['-SEARCH QUERY-']:
                # Trigger search when Enter is pressed
                event = 'Search'
                # Remove the newline from the query
                query_text = values['-SEARCH QUERY-'].replace('\r', '').replace('\n', '')
                window['-SEARCH QUERY-'].update(query_text)
                # Manually call the search handler
                query = query_text
                if not query.strip():
                    sg.popup_error("Please enter a search query.", keep_on_top=True)
                elif not os.path.exists(bm25_index_path):
                    sg.popup_error("No BM25 index found. Please build an index first.", keep_on_top=True)
                else:
                    try:
                        log_print(f"Searching for: '{query}'")
                        # Perform BM25 search
                        results = query_bm25(query=query, index_path=bm25_index_path, num_results=10)
                        
                        # Format results for display
                        search_results = []
                        if results['text'] and len(results['text']) > 0:
                            for i, (text, chunk_id) in enumerate(zip(results['text'], results['id'])):
                                # Clean up text for display - remove extra whitespace and newlines
                                clean_text = ' '.join(text.split())
                                # Truncate text for display in listbox
                                display_text = clean_text[:150] + "..." if len(clean_text) > 150 else clean_text
                                search_results.append(f"[{i+1}] Chunk {chunk_id}: {display_text}")
                            
                            # Update the search results listbox
                            window['-SEARCH RESULTS-'].update(search_results)
                            log_print(f"Found {len(search_results)} results for query: '{query}'")
                        else:
                            # No results found
                            window['-SEARCH RESULTS-'].update(["No results found for your query."])
                            log_print(f"No results found for query: '{query}'")
                        
                    except Exception as e:
                        error_msg = f"Error performing search: {str(e)}"
                        sg.popup_error(error_msg, keep_on_top=True)
                        log_print(error_msg)
                        # Clear results on error
                        window['-SEARCH RESULTS-'].update([f"Error: {str(e)}"])

        elif event == '-SEARCH RESULTS-':
            # Handle search result selection
            if values['-SEARCH RESULTS-']:
                selected_result = values['-SEARCH RESULTS-'][0]
                # Show more detail of the selected result
                try:
                    # Extract chunk ID from the selected result
                    if "Chunk " in selected_result:
                        chunk_id_str = selected_result.split("Chunk ")[1].split(":")[0]
                        # For now, just show a popup with the selected result
                        sg.popup_scrolled("Selected Result", selected_result, 
                                        size=(80, 20), keep_on_top=True)
                except Exception as e:
                    log_print(f"Error showing result details: {e}")

        elif event == "Set Theme":
            if values['-THEME LISTBOX-']:
                theme_chosen = values['-THEME LISTBOX-'][0]
                window.close()
                window = make_window(theme_chosen)

        elif event == 'Edit Me':
            sg.execute_editor(__file__)
            
        elif event == 'Versions':
            sg.popup_scrolled(__file__, sg.get_versions(), keep_on_top=True, non_blocking=True)

    window.close()
    log_print("Application closed")

if __name__ == '__main__':
    main()