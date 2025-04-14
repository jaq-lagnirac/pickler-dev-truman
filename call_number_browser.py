# Justin Caringal
# 
# A program that takes in input call number in the system and finds 
# call numbers which precede and succeed around an input
# 
# Project start date: 2025-02-10
# Project end date: 2025-04-07 (initial, tentative)

### LIBRARIES / PACKAGES ###

import os
import sys
import json
import tkinter as tk
import webbrowser as wb
from bisect import bisect
from time import sleep
import folioclient
from PIL import ImageTk, Image
import pycallnumber as pycn
from pycallnumber.units import callnumbers
from pycallnumber.units.simple import Alphabetic
from pycallnumber.units.numbers import Number
from pycallnumber.exceptions import InvalidCallNumberStringError

### GLOBAL CONSTANTS / VARIABLES ###

REPO_LINK = 'https://library.truman.edu'
SUCCESS_COL = '#00dd00'
FAIL_COL = '#ff0000'
DEFAULT_COL = '#000000'
FONT_TUPLE = ('Verdana', 10)
LOGO_PATH = os.path.join('images', 'logo-no-background.png')
HELP_PATH = os.path.join('texts', 'info-help-text.txt')
OUTPUT_BOX_INIT_PATH = os.path.join('texts', 'output-box-initial-text.txt')
DUMMY_TITLE_TEXT = f'<{'-' * 10}Inputted call number{'-' * 10}<'
CALL_NUM_BUFFER = 40
TITLE_BUFFER = 45
LINE_LENGTH = CALL_NUM_BUFFER + TITLE_BUFFER
SLICE_ONE_SIDED = 10

# scope resolution for variable used in
# login_folioclient and start_call_num_search
tenant = None

# scope resolution for global variable used
# as comparison against extracted call numbers
input_call_num_type = None # scope resolution

# keys required in config.json
REQUIRED_CONFIG_KEYS = {
    'okapi_url' : 'https://okapi-mobius.folio.ebsco.com',
    'tenant' : '[INSTITUTION ID]',
    'username' : '[USERNAME]',
    'password' : '[PASSWORD]',
}

### FUNCTIONS ###

def resource_path(relpath : str) -> str:
    """Finds external resource for onefile pyinstaller executable.
    
    A function which generates a new relative path for external data,
    (i.e. images) during execution, mainly for use when creating an
    executable with PyInstaller.

    Based off of the following StackOverflow forum post:
    https://stackoverflow.com/a/72060275

    Args:
        relpath (str): a relative path to the file in question
    
    Returns:
        str: Returns a new path to the file
    """

    # https://stackoverflow.com/a/72060275
    try:
        base_path = sys._MEIPASS # only found in PyInstaller
    except AttributeError:
        base_path = os.curdir

    return os.path.join(base_path, relpath)


def error_msg(msg : str = 'Unknown error occured.') -> None:
    """Pops up to user and shows error.
    
    A function which organizes the creation of a TKinter box
    to show error and clean-up operations, after which the
    system exits and terminates the program.
    
    Args:
        msg (str): the message the user sees
        
    Returns:
        None, terminates program
    """

    # displays error window
    error = tk.Toplevel()
    error.title('Error')
    tk.Label(error, text=msg, justify='left').grid(row = 0, column = 1)
    error_cancel = tk.Button(error,
                             text='Cancel',
                             width=25,
                             command=error.destroy)
    error_cancel.grid(row=1, column=1)
    error.mainloop()


def is_juvenile_fiction(call_number : callnumbers.local.Local) -> bool:
    """Works out if call number is a Juvenile Fiction call number.

    A function which returns True if the call number is
    a Juvenile Fiction Dewey Decimal number, False otherwise.
    Created specifically for Pickler Memorial Library,
    but may work within other libraries' systems.

    Args:
        call_number (callnumbers.local.Local): the inputted call number

    Returns:
        bool: Returns True if call number is for a Juvenile
            Fiction Dewey Decimal number, False otherwise.
    """

    if len(call_number.parts) != 4:
        return False

    fiction = pycn.callnumber('F')
    if call_number.parts[0] != fiction: # must begin with 'F'
        return False
    
    if type(call_number.parts[1]) != Alphabetic:
        return False
    
    if type(call_number.parts[2]) != Number:
        return False
    
    if type(call_number.parts[3]) != Alphabetic:
        return False
    
    return True


def update_validation(*entry : tk.Event) -> bool:
    """Updates id_validation_msg based off of input.
    
    A function which updates a tkinter Label based off of
    the input to the id_validation_msg Entry.

    Based off of the following StackOverflow forum post:
    https://stackoverflow.com/a/73126296
    
    Args:
        entry (str): The user-inputted entry, not interacted with
    
    Returns:
        bool: Returns True if patron ID is valid, False otherwise
    """

    global input_call_num_type

    # retrieves patron id from text field
    call_num = call_num_input.get().upper().strip()

    # function validates to ensure call number is inputted
    is_valid_id = False # default case
    try:
        call_num = pycn.callnumber(call_num)
        input_call_num_type = type(call_num)
        if input_call_num_type == callnumbers.lc.LC:
            status.config(text='Valid LC call number.',
                          fg=SUCCESS_COL)
        elif input_call_num_type == callnumbers.dewey.Dewey:
            status.config(text='Valid Dewey call number.',
                          fg=SUCCESS_COL)
        elif is_juvenile_fiction(call_num):
            status.config(text='Valid Juvenile Fiction call number.',
                          fg=SUCCESS_COL)
        else:
            raise InvalidCallNumberStringError 
        enter_button.config(state='normal')
        is_valid_id = True

    except (InvalidCallNumberStringError, AttributeError):
        status.config(text='Please input a valid LC or Dewey call number.',
                      fg=FAIL_COL)
        enter_button.config(state='disabled')

    # wrap-up statements
    root.update()
    return is_valid_id


def update_status(*, # requires all arguments to be keyword-only arguments
                  msg : str = '',
                  col : str = DEFAULT_COL,
                  enter_state : str = None) -> None:
    """Updates the status message on the main root window.
    
    A function which handles the status message returned to the user
    during "main" function execution. Also handles the enabling
    and disabling of the button, defaulting to leaving the button
    alone if no input is given.
    
    Args:
        msg (str): The message to be sent to the user
        col (str): Color hexcode of the text, defaults to
            DEFAULT_COL (black)
        enter_state (str): The requested updated state of
            the enter button, defaults to keeping 

    Returns:
        None
    """

    # changes status message if it is inputted,
    # otherwise keep it the same
    if msg:
        status.config(text=msg, fg=col)
    
    # changes enter button state if requested,
    # otherwise keep it the same
    if enter_state:
        enter_button.config(state=enter_state)

    root.update()
    return


def open_info_help() -> None:
    """Opens a special info/help window.
    
    A function which extracts text from an external .txt file and displays
    the relevant info/help information.

    Args:
        None
    
    Returns:
        None
    """

    # initializes edge alignment for textbox and cancel button
    INFO_X_PADDING = 20

    # initializes start-up
    info_window = tk.Toplevel()
    info_window.resizable(False, False)
    info_window.title('Info/Help')

    # adds logo image
    INFO_IMAGE_MULTIPLIER = 1
    info_image = Image.open(resource_path(LOGO_PATH)) # opens image
    info_image = info_image.resize(size=[int(INFO_IMAGE_MULTIPLIER * \
                                             length) \
                                         for length in image.size])
    # converts image to format usable by Tkinter
    info_logo = ImageTk.PhotoImage(info_image)
    tk.Label(info_window, image=info_logo).grid(row=0,
                                                column=0,
                                                columnspan=3)

    # creates text widget
    info_textbox = tk.Text(info_window,
                           wrap='word',
                           font=('Courier New', FONT_TUPLE[1]))
    info_textbox.grid(row=1,
                      column=0,
                      columnspan=3,
                      padx=(INFO_X_PADDING, INFO_X_PADDING))

    # creates scrollbar
    info_scrollbar = tk.Scrollbar(info_window)
    info_scrollbar.grid(row=0,
                        column=100,
                        rowspan=100,
                        sticky='NS')

    # configures text widget to use scrollbar
    info_textbox.config(yscrollcommand=info_scrollbar.set)
    info_scrollbar.config(command=info_textbox.yview)

    # adds text to text widget
    info_txt_path = resource_path(HELP_PATH)
    info_text = None # scope resolution
    with open(info_txt_path, 'r') as file:
        info_text = file.read()
    info_textbox.insert('end', info_text) # needs to be before text disable
    info_textbox.config(state='disabled') # disables editing of help text

    # adds button to repository documentation
    INFO_Y_PADDING_TUPLE = (10, 20)
    repo_button = tk.Button(info_window,
                            text='More...',
                            command=lambda: wb.open(REPO_LINK, new=1))
    repo_button.grid(row=2,
                     column=1,
                     sticky='NESW',
                     pady=INFO_Y_PADDING_TUPLE)
    # adds button to close help window
    cancel_info_button = tk.Button(info_window,
                                   text='Cancel',
                                   command=info_window.destroy)
    cancel_info_button.grid(row=2,
                            column=2,
                            sticky='NESW',
                            padx=(0, INFO_X_PADDING),
                            pady=INFO_Y_PADDING_TUPLE)

    info_window.mainloop()


def login_folioclient() -> folioclient.FolioClient:
    """Organizes initial handshake with FOLIOClient.
    
    A function which handles the possible exceptions on start-up
    and, if everything is in order, logs into the FOLIOClient API.
    
    Args:
        None
    
    Returns:
        FolioClient: Returns an API object to the FOLIOClient
    """

    global tenant

    config_name = config_relpath.get()

    # checks for existence of config.json file, notifies user if none available
    if not os.path.exists(config_name):
        with open(config_name, 'w') as config_template:
            json.dump(REQUIRED_CONFIG_KEYS, config_template, indent=4)
        status_msg = f'\"{config_name}\" not detected.'
        update_status(msg=status_msg,
                      col=FAIL_COL)
        error_msg(f'{status_msg} Creating template \"{config_name}\".')
        return

    # Setup FOLIO variables
    login = None # scope resolution
    with open(config_name ,'r') as config:
        login = json.load(config)

    # checks to ensure config file is set up correctly
    required_key_names = set(REQUIRED_CONFIG_KEYS.keys())
    # if required keys not in login
    if not required_key_names.issubset(set(login.keys())):
        update_status(msg=f'\"{config_name}\" improperly set up.',
                      col=FAIL_COL)
        error_msg(f'\"{config_name}\" improperly set up.\nPlease check keys.' \
                  f'\nDetected keys: {set(login.keys())}' \
                  f'\nRequired keys: {required_key_names}')
        return

    # unpacks relevant data from config.json file
    okapi_url = login['okapi_url']
    tenant = login['tenant']
    username = login['username']
    password = login['password']

    # attempts FOLIO API handshake
    f = None # scope resolution
    try:
        f = folioclient.FolioClient(okapi_url, tenant, username, password)
    except Exception as e:
        status_msg = f'Cannot connect to FolioClient. Try again.'
        update_status(msg=status_msg,
                      col=FAIL_COL,
                      enter_state='normal')
        error_msg(f'{status_msg}\n{e}')

    return f


def extract_queries(queries : list,
                    total_records : int) -> list:
    """Extracts FOLIO information into a list.
    
    A function which takes a list from the FOLIO
    API folio_get method and extracts the relevant
    information into a dictionary which is then appended to
    a return list.

    Args:
        queries (list): A FOLIO list containing call number information
        total_records (int): The total count of records listed (NOT items)
    
    Returns:
        list: A list of the relevant extracted information stored
            in separate dictionaries.
    """

    extracted_items = [] # the list to be returned

    for index, query in enumerate(queries):
        queries_processed_txt = f'{index}/{total_records}' \
            ' call numbers processed.'
        try:
            update_status(msg=queries_processed_txt)
        except tk.TclError:
            # safely ends function in case of premature window closure
            sys.exit(1)

        title = query['title'] # the same across the board
        items = query['items'] # a dictionary of further key-values
        
        # iterates through each separate item tied to a holding
        #
        # brute forces finding LC call numbers, because Pickler
        # uses both LC and Dewey call numbers (for some reason)
        for item in items:
            item_info = {
                'title' : title,
                'callNumber' : 'n/a',
                'shelvingOrder' : 'n/a' # for sorting
            }

            call_num_components = item['effectiveCallNumberComponents']
            extracted_call_num_type = None # scope resolution
            try: # replaces "if 'callNumber' in call_num_components:"
                call_num = pycn.callnumber(call_num_components['callNumber'])
                item_info['callNumber'] = call_num
                extracted_call_num_type = type(call_num)
            except Exception: # catches all exceptions, not just KeyErrors
                ...

            if 'effectiveShelvingOrder' in item:
                item_info['shelvingOrder'] = item['effectiveShelvingOrder']

            if input_call_num_type == extracted_call_num_type:
                extracted_items.append(item_info)
    
    return extracted_items


def remove_duplicates(items : list) -> list:
    """Removes duplicates from a list of dictionaries.
    
    A function which processes a list of dictionaries and removes any
    duplicates while still maintaining a sorted order.
    
    Args:
        items (list): a list of items to be trimmed
    
    Returns:
        list: A trimmed list of items with no duplicates
    """

    seen = set() # items already seen
    trimmed_items = [] # unique items to be returned
    for item in items:
        
        # converts key-values into hashable pairs to be added to the list
        hashable_pair = tuple(sorted(item.items()))
        
        if hashable_pair not in seen:
            seen.add(hashable_pair) # adds hashable pair to set
            trimmed_items.append(item) # adds full item to list

    return trimmed_items


def extract_slice(items : list,
                  call_number : callnumbers.lc.LC) -> list:
    """Identifies insertion point of call number into lst.
    
    A function which finds where a call number goes into a list
    and returns a list of the call number as well as the items
    preceeding and succeeding it.
    
    Args:
        items (list): A list of dictionaries with item information
        call_number (LC): The number to be inserted
    
    Returns:
        list, bool, bool: Returns a slice of the original slice
            surrounding the insertion point of the call number,
            as well as if the slice overlaps with the start/end
            out of bounds areas of the original list
    """

    dummy_dict = {
        'callNumber': call_number,
        'shelvingOrder' : '',
        'title' : DUMMY_TITLE_TEXT,
    }

    search_key = lambda info : (info['callNumber'])
    insertion_point = bisect(items, call_number, key=search_key)
    items.insert(insertion_point, dummy_dict)

    # scope resolution, default case
    start_out_of_bounds = False
    end_out_of_bounds = False

    start_index = insertion_point - SLICE_ONE_SIDED
    if start_index < 0: # check required to handle bottoming out
        start_index = 0
        start_out_of_bounds = True

    # no top end check/reassignment needed, python handles it internally
    #
    # +1 for half-open indexing [ )
    end_index = insertion_point + SLICE_ONE_SIDED + 1
    if end_index > (len(items) - 1):
        end_out_of_bounds = True

    return items[start_index : end_index], \
        start_out_of_bounds, \
        end_out_of_bounds


def print_call_num_slice(item_slice : list,
                         start_out_of_bounds : bool,
                         end_out_of_bounds : bool) -> None:
    """Formats the call number slice output.
    
    Formats and prints the call number slice from the extracted,
    sorted, and trimmed item list.
    
    Args:
        item_slice (list):
        start_out_of_bounds (bool): Is True if slice goes out
            of bounds at the start of the list (index < 0)
        end_out_of_bounds (bool): Is True if slice goes out
            of bounds at the end of the list (index >= len)

    Returns:
        None
    """

    global input_call_num_type
    call_num_header = ' (Juvenile Fiction)' # default
    if input_call_num_type == callnumbers.lc.LC:
        call_num_header = ' (Library of Congress)'
    elif input_call_num_type == callnumbers.dewey.Dewey:
        call_num_header = ' (Dewey Decmial)'

    # sets up output header
    output_heading = f'{f'CALL NUMBER{call_num_header}':<{CALL_NUM_BUFFER}}' \
        f'{'TITLE':<{TITLE_BUFFER}}\n'
    output_txt = f'{output_heading}{'-' * LINE_LENGTH}\n'
    
    # sets up out of bounds check for starting string
    if start_out_of_bounds:
        output_txt += '>>>START OF FILE<<<\n'
    
    # adds call numbers and titles from slice
    for item in item_slice:

        # extracts information
        call_num = item['callNumber'].for_print()
        title = item['title'][ : TITLE_BUFFER]

        # adds different formatting for inputted call num placement
        num_buffer = CALL_NUM_BUFFER
        if title == DUMMY_TITLE_TEXT:
            num_buffer -= 3

        # adds call number and title to output string
        output_txt += f'{call_num:<{num_buffer}}{title:<{TITLE_BUFFER}}\n'

    # sets up out of bounds check for ending string
    if end_out_of_bounds:
        output_txt += '>>>>END OF FILE<<<<'
    
    # clears output textbox of previous outputs
    call_num_slice_textbox.config(state='normal')
    call_num_slice_textbox.delete(1.0, 'end')
    call_num_slice_textbox.config(state='disabled')

    update_status(msg='Success! Listing call numbers...',
                  col=SUCCESS_COL)
    # prints call numbers character by character
    for char in output_txt:
        try:
            call_num_slice_textbox.config(state='normal')
            call_num_slice_textbox.insert('end', char)
            call_num_slice_textbox.config(state='disabled')
            root.update()
            sleep(0.0005)
        except tk.TclError:
            return # safely ends function in case of premature window closure
    
    return # ends function


def start_call_num_search() -> None:
    """The response to clicking the Enter button.
    
    A function which validates the user inputs,
    organizes the login actions to FolioClient,
    and handles the call number browser.

    Serves as the "main" function after Enter is clicked.
    
    Args:
        None
    
    Returns:
        None
    """

    # logs into folioclient
    update_status(msg='Logging into FOLIO.',
                  enter_state='disabled')
    f = login_folioclient()
    if not f:
        # safety net to enable enter button again,
        # more detailed status messages executed during
        # login_folioclient() execution
        update_status(enter_state='normal')
        return

    update_status(msg='Querying FOLIO API.')
    # takes input from user and files
    global tenant
    call_number = call_num_input.get()
    call_number = call_number.upper().strip() # cleans and standardizes data
    call_number = pycn.callnumber(call_number)
    classification = None # scope resolution
    if type(call_number) == callnumbers.lc.LC:
        classification = call_number.classification.letters
    elif type(call_number) == callnumbers.dewey.Dewey:
        classification = call_number.classification
    elif is_juvenile_fiction(call_number):
        classification = f'{call_number.parts[0]} {call_number.parts[1]}'
    else:
        update_status(msg='Something went wrong with the ' \
                      'inputted call number, please try again.',
                      col=FAIL_COL)
        return

    # formats search query
    search_query = f'holdings.tenantId=\"{tenant}\"' \
        f' and holdingsNormalizedCallNumbers==\"{classification}\"' \
        ' and staffSuppress==\"false\"'
    # makes the queries
    total_records = f.folio_get(path='/search/instances',
                                key='totalRecords',
                                query=search_query)
    queries = f.folio_get(path='/search/instances',
                          key='instances',
                          query=search_query)
    
    # a list of call number information from a FOLIO list
    call_num_input.delete(0, 'end')
    update_status(msg='Extracting items from FOLIO.')
    extracted_items = extract_queries(queries, total_records)

    # sorts the list
    update_status(msg='Sorting extracted items.')
    sorting_reqs = lambda info : (info['callNumber'])
    sorted_items = sorted(extracted_items, key=sorting_reqs)

    # trims duplicates from list
    update_status(msg='Trimming duplicates.')
    trimmed_items = remove_duplicates(sorted_items)
    
    # finds where to put inputted call number
    update_status(msg='Extracting call number slice.')
    list_slice, \
        start_is_oob, \
        end_is_oob \
        = extract_slice(trimmed_items, call_number) # oob == out of bounds
    
    print_call_num_slice(list_slice, start_is_oob, end_is_oob)
    success_msg = f'Success! Done printing slice around \"{call_number}\".'
    update_status(msg=success_msg,
                  col=SUCCESS_COL)

    return


# Justin Caringal, TSU, BSCS 2025, github@jaq-lagnirac
# main loop functionality, generates root tkinter window
# where most of the user interacts
if __name__ == '__main__':
    BUTTON_COUNT = 3
    INPUT_WIDTH = 60
    DEFAULT_CONFIG_NAME = os.path.join(os.getcwd(), 'config.json')
    X_WIDGET_PADDING = 20
    TEXT_SIDE_PADDING = (X_WIDGET_PADDING, 0)
    INPUT_SIDE_PADDING = (0, X_WIDGET_PADDING)

    root = tk.Tk()
    root.resizable(False, False)
    root.title('Call Number Browser')

    # formats "splash header"
    IMAGE_ROW = 0
    IMAGE_COLUMN = 0
    IMAGE_MULTIPLIER = 0.3
    image = Image.open(resource_path(LOGO_PATH)) # opens image
    image = image.resize(size=[int(IMAGE_MULTIPLIER * length) \
                               for length in image.size])
    # converts image to format usable by Tkinter
    logo = ImageTk.PhotoImage(image)
    tk.Label(root, image=logo).grid(row=IMAGE_ROW,
                                    column=IMAGE_COLUMN,
                                    columnspan=100,
                                    padx=(X_WIDGET_PADDING, X_WIDGET_PADDING),
                                    pady=(10, 0))

    # requests path of config.json
    CONFIG_ROW = IMAGE_ROW + 1
    CONFIG_COLUMN = IMAGE_COLUMN
    config_txt = tk.Label(root,
                          text='Path to configuration file:\t',
                          font=FONT_TUPLE)
    config_txt.grid(sticky='W',
                    row=CONFIG_ROW,
                    column=CONFIG_COLUMN,
                    padx=TEXT_SIDE_PADDING)
    config_relpath = tk.Entry(root,
                              width=INPUT_WIDTH)
    config_relpath.grid(sticky='NESW',
                        row=CONFIG_ROW,
                        column=CONFIG_COLUMN + 1,
                        columnspan=BUTTON_COUNT,
                        padx=INPUT_SIDE_PADDING)
    config_relpath.insert(0, DEFAULT_CONFIG_NAME) # default value

    # requests call number
    CALL_NUM_ROW = CONFIG_ROW + 1
    CALL_NUM_COLUMN = IMAGE_COLUMN
    call_num_txt = tk.Label(root,
                            text='Call number:\t',
                            font=FONT_TUPLE)
    call_num_txt.grid(sticky='W',
                      row=CALL_NUM_ROW,
                      column=CALL_NUM_COLUMN,
                      padx=TEXT_SIDE_PADDING)
    call_num_string = tk.StringVar()
    call_num_input = tk.Entry(root,
                              width=INPUT_WIDTH,
                              textvariable=call_num_string)
    call_num_input.grid(sticky='NESW',
                        row=CALL_NUM_ROW,
                        column=CALL_NUM_COLUMN + 1,
                        columnspan=BUTTON_COUNT,
                        padx=INPUT_SIDE_PADDING)
    # new error handling with increased response time
    # https://stackoverflow.com/a/51421764    
    call_num_string.trace_add('write', update_validation)
    # adds Enter/Return in the call num input as an option to start program
    validate_and_start = lambda *_ : start_call_num_search() \
        if update_validation() else None
    call_num_input.bind('<Return>', validate_and_start)

    # bottom rows
    BOTTOM_ROW = 100 # arbitrarily large number
    BUTTON_ROW = BOTTOM_ROW - 10
    STATUS_ROW = BUTTON_ROW - 5
    OUTPUT_ROW = STATUS_ROW + 1
    BUTTON_COLUMN_START = IMAGE_COLUMN + 1
    STATUS_FONT = ('Courier New', 11)
    status = tk.Label(root, text='', font=STATUS_FONT)
    status.grid(sticky='W',
                row=STATUS_ROW,
                column=IMAGE_COLUMN,
                columnspan=100,
                padx=TEXT_SIDE_PADDING,
                pady=(12, 12))
    # creates text widget
    call_num_slice_textbox = tk.Text(root,
                                     wrap='word',
                                     font=('Courier New', FONT_TUPLE[1]),
                                     height=25,
                                     width=90)
    call_num_slice_textbox.grid(row=OUTPUT_ROW,
                                column=IMAGE_COLUMN,
                                columnspan=BUTTON_COUNT + 1,
                                padx=(X_WIDGET_PADDING, X_WIDGET_PADDING),
                                pady=(0, 10))
    starting_txt = '' # scope resolution, default
    init_txt_path = resource_path(OUTPUT_BOX_INIT_PATH)
    with open(init_txt_path, 'r') as init_txt_file:
        starting_txt = init_txt_file.read()
    call_num_slice_textbox.insert('end', starting_txt)
    call_num_slice_textbox.config(state='disabled')
    # creates scrollbar
    slice_scrollbar = tk.Scrollbar(root)
    slice_scrollbar.grid(row=0,
                         column=100,
                         rowspan=100,
                         sticky='NS')
    # configures text widget to use scrollbar
    call_num_slice_textbox.config(yscrollcommand=slice_scrollbar.set)
    slice_scrollbar.config(command=call_num_slice_textbox.yview)
    # NOTE: sticky='NESW' used to fill box to fit column and row
    enter_button = tk.Button(root,
                             text='Enter',
                             command=start_call_num_search)
    enter_button.grid(sticky='NESW',
                      row=BUTTON_ROW,
                      column=BUTTON_COLUMN_START)
    enter_button.config(state='disabled') # default state is disabled
    help_button = tk.Button(root,
                            text='Info/Help',
                            command=open_info_help)
    help_button.grid(sticky='NESW',
                     row=BUTTON_ROW,
                     column=BUTTON_COLUMN_START + 1)
    cancel_button = tk.Button(root,
                              text='Cancel',
                              command=root.destroy)
    cancel_button.grid(sticky='NESW',
                       row=BUTTON_ROW,
                       column=BUTTON_COLUMN_START + 2,
                       padx=(0, X_WIDGET_PADDING))
    
    # bottom credits
    description = tk.Label(root,
                           text='\nDeveloped by Technical Services ' \
                            '& Systems, Pickler Memorial Library, ' \
                            'Truman State University, MO, 2024\n' \
                            'Raw ver. info.: Z2l0aHViQGphcS1sYWduaXJhYw==',
                           justify='left',
                           font=(FONT_TUPLE[0], 7))
    description.grid(sticky='W', row=BOTTOM_ROW, column=0, columnspan=100)

    root.mainloop()