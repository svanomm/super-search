import os
from file_scanner import file_scanner
from chunk_db import chunk_db
from create_bm25_index import create_bm25_index
from query_bm25 import query_bm25
import FreeSimpleGUI as sg

def make_window(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['E&xit']],
                ['&Help', ['&About']] ]
    right_click_menu_def = [[], ['Edit Me', 'Versions', 'Nothing','More Nothing','Exit']]
    graph_right_click_menu_def = [[], ['Erase','Draw Line', 'Draw',['Circle', 'Rectangle', 'Image'], 'Exit']]

    input_layout =  [
                # [sg.Menu(menu_def, key='-MENU-')],
                [sg.Text('This tab is for creating search indices/databases.')], 
                [sg.Text('Input your filepath to the directory to index.')], 
                [sg.Button("Open Folder to Index"), sg.Text("", key='-INDEX DIRECTORY-')], 
                [sg.Text('If you want to specify your index location, or already have one, put it below.')], 
                [sg.Button("Open Database Folder")],
                [sg.Checkbox('Create semantic index in addition to BM25', default=False, k='-CREATE_SEMANTIC_INDEX-')],
                [sg.Text('Files to index:')],
                [sg.Multiline("", size=(45,4), expand_x=True, expand_y=False, horizontal_scroll=True, k='-FILELIST_DISPLAY-')],
                [sg.Button('Build Index', key='-BUILD_INDEX-'), sg.Button('Update Index', key='-UPDATE_INDEX-'), sg.Button(image_data=sg.DEFAULT_BASE64_ICON, key='-LOGO-')]]

    search_layout = [
                    [sg.Text('This tab is for searching your indexed files.')],
                    [sg.Text('Index Status: No index loaded', key='-INDEX STATUS-')],
                    [sg.Text('Input your search query below:')],
                    [sg.Input(key='-SEARCH QUERY-', size=(40, 1), enable_events=True)],
                    [sg.Button('Search'), sg.Button('Clear Search')],
                    [sg.Text('Search Results:')],
                    [sg.Listbox(values=[], size=(60, 10), key='-SEARCH RESULTS-', expand_x=True, expand_y=True, enable_events=True, horizontal_scroll=True)],
                    [sg.Button('Test Progress Bar'), sg.ProgressBar(100, orientation='h', size=(20, 20), key='-PROGRESS BAR-')]
                    ]

    logging_layout = [[sg.Text("Anything printed will display here!")],
                      [sg.Multiline(size=(60,15), font='Courier 8', expand_x=True, expand_y=True, write_only=True,
                                    reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True, autoscroll=True, auto_refresh=True)]
                      # [sg.Output(size=(60,15), font='Courier 8', expand_x=True, expand_y=True)]
                      ]
    popup_layout = [[sg.Text("Popup Testing")],
                    [sg.Button("Open Folder")],
                    [sg.Button("Open File")]]

    layout = [ [sg.MenubarCustom(menu_def, key='-MENU-', font='Courier 15', tearoff=True)],
                [sg.Text('A Local Search Engine with Semantic Capabilities', size=(20, 1), justification='left', font=("Helvetica", 16), relief=sg.RELIEF_RIDGE, expand_x=True, k='-TEXT HEADING-', enable_events=True)]]
    layout +=[[sg.TabGroup([[  sg.Tab('Input', input_layout),
                               sg.Tab('Search', search_layout),
                               sg.Tab('Output', logging_layout)]], key='-TAB GROUP-', expand_x=True, expand_y=True),
               ]]
    layout[-1].append(sg.Sizegrip())
    window = sg.Window('super-search', layout, right_click_menu=right_click_menu_def, right_click_menu_tearoff=True, grab_anywhere=True, resizable=True, margins=(0,0), use_custom_titlebar=True, finalize=True, keep_on_top=True)
    window.set_min_size(window.size)
    return window
