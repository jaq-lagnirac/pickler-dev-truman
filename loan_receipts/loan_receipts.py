# Justin Caringal, Stephen Wynn
# 
# A program to that generates and prints out the receipts for
# library patrons. Intended for Pickler Memorial Library interal
# use, may be eventually extended to outside use.
# 
# Project start date: 2024-10-21
# Project end date: YYYY-MM-DD

### LIBRARIES / PACKAGES ###

import os
import sys
import json
import tkinter as tk
import webbrowser as wb
from datetime import datetime, timezone, timedelta
from typing import Generator
import folioclient
from PIL import ImageTk, Image

### GLOBAL CONSTANTS / VARIABLES ###

REPO_LINK = 'https://library.truman.edu'
SUCCESS_COL = '#00dd00'
FAIL_COL = '#ff0000'
DEFAULT_COL = '#000000'
FONT_TUPLE = ('Verdana', 10)
LOGO_PATH = os.path.join('images', 'logo-no-background.png')
HELP_PATH = os.path.join('texts', 'info-help-text.txt')


# keys required in config.json
REQUIRED_CONFIG_KEYS = {
    'okapi_url',
    'tenant',
    'username',
    'password',
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
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

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
    tk.Label(error, text = msg).grid(row = 0, column = 1)
    button = tk.Button(error, text = 'Cancel', width=25, command = error.destroy)
    button.grid(row = 1, column = 1)
    error.mainloop()


def update_validation(*entry : tk.Event) -> None:
    """Updates id_validation_msg based off of input.
    
    A function which updates a tkinter Label based off of
    the input to the id_validation_msg Entry.

    Based off of the following StackOverflow forum post:
    https://stackoverflow.com/a/73126296
    
    Args:
        entry (str): The user-inputted entry, not interacted with
    
    Returns:
        None
    """

    # retrieves patron id from text field
    patron_id = id_input.get()

    if patron_id.isdigit():
        status.config(text='Valid Patron ID.',
                      fg=SUCCESS_COL)
        enter_button.config(state='normal')
    else:
        status.config(text='Patron ID must be a numerical value.',
                      fg=FAIL_COL)
        enter_button.config(state='disabled')
    root.update()
    return


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

    # changes status message
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

    # initializes edge alignment for text box and cancel button
    INFO_X_PADDING = 20

    # initializes start-up
    info_window = tk.Toplevel()
    info_window.resizable(False, False)
    info_window.title('Info/Help')

    # adds logo image
    INFO_IMAGE_MULTIPLIER = 1
    info_image = Image.open(resource_path(LOGO_PATH)) # opens image
    info_image = image.resize(size=[int(INFO_IMAGE_MULTIPLIER * length) for length in image.size])
    info_logo = ImageTk.PhotoImage(info_image) # converts image to format usable by Tkinter
    tk.Label(info_window, image=info_logo).grid(row=0, column=0, columnspan=3)

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
    info_scrollbar.grid(row=0, column=100, rowspan=100, sticky='NS')

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

    config_name = config_relpath.get()

    # checks for existence of config.json file, notifies user if none available -jaq
    if not os.path.exists(config_name):
        status_msg = f'\"{config_name}\" not detected.'
        update_status(msg=status_msg,
                      col=FAIL_COL)
        error_msg(status_msg)

    # Setup FOLIO variables
    login = None # scope resolution
    with open(config_name ,'r') as config:
        login = json.load(config)

    # checks to ensure config file is set up correctly -jaq
    if not REQUIRED_CONFIG_KEYS.issubset(set(login.keys())): # if required keys not in login
        update_status(msg=f'\"{config_name}\" improperly set up.',
                      col=FAIL_COL)
        error_msg(f'\"{config_name}\" improperly set up.\nPlease check keys.' + \
                  f'\nDetected keys: {set(login.keys())}' + \
                  f'\nRequired keys: {REQUIRED_CONFIG_KEYS}')

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

def extract_queries(queries : Generator[str, str, None],
                    patron_id : str) -> list:
    """Extracts queries from FOLIO object.
    
    A function which iterates through a FOLIO object and compares
    it against the patron ID inputted by the user. If the borrower
    barcode matches the patron ID, add an extracted info dictionary
    to a list to be returned by the function.
    
    Args:
        queries (Generator): A non-iterable object returned by FOLIO
        patron_id (str): The inputted patron ID to be compared against
    
    Returns:
        list: Returns a list of dictionaries containing item information
    """

    checked_out_items = [] # list of dicts to be returned

    for query in queries:
        # extracts patron ID associated with query
        barcode_borrower = query['borrower']['barcode']

        # if barcode matches inputted patron ID, extract info from query
        if barcode_borrower == patron_id:
            # extracts due date, coverts to a more human-readable format
            # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
            iso_due_date = datetime.fromisoformat(query['dueDate'])
            iso_due_date = iso_due_date.astimezone() # defaults to system timezone
            printable_due_date = iso_due_date.strftime('%a %d %b %Y, %I:%M%p')

            # extracting and bundling the needed item information
            item = query['item']
            item_info = {
                'title' : item['title'],
                'barcode' : item['barcode'],
                'dueDate' : printable_due_date,
            }
            try:
                item_info['callNumber'] = item['callNumber']
            except KeyError:
                item_info['callNumber'] = 'n/a'
            checked_out_items.append(item_info)

    return checked_out_items


def start_receipt_printing() -> None:
    """The response to clicking the Enter button.
    
    A function which validates the user inputs,
    organizes the login actions to FolioClient,
    and handles the loan receipt printing.

    Serves as the "main" function after Enter is clicked.
    
    Args:
        None
    
    Returns:
        None
    """

    # prevents future inputs
    update_status(msg='Beginning receipt printing. Logging into FOLIO.',
                  enter_state='disabled')
    
    # logs into folioclient
    f = login_folioclient()
    if not f:
        # safety net to enable enter button again,
        # more detailed status messages executed during
        # login_folioclient() execution
        update_status(enter_state='normal')
        return
    
    # generates 15-min timeframe for search and comparison
    time_now = datetime.now(timezone.utc) # gets current UTC time
    search_window = timedelta(days=7, minutes=15) # creates 15-min window
    timeframe_start = time_now - search_window # calculates start of search
    iso_timeframe = timeframe_start.isoformat() # converts to ISO 8601

    # searches for all checkouts in the last 15 mins
    # NOTE: There is apparently a CQL way to query the borrower.barcode
    # specifically, however no one here (including myself) knows how to
    # conduct a query on a nested object in CQL. If someone knows how to
    # do that they definitely should, and can remove the (now unnecessary)
    # if statement in extract_queries(). Until then, this program will be
    # slightly more inefficient by a few milliseconds (aw schucks, lost time).
    # We tried 'borrower.barcode == \"{patron_id}\"', but that didn't work for
    # some reason (probably my own glaring lack of knowledge of CQL). -jaq
    # https://dev.folio.org/reference/api/endpoints/
    update_status(msg='Querying FOLIO API.')
    search_query = f'loanDate > \"{iso_timeframe}\" and action == \"checkedout\"'
    queries = f.folio_get_all(path='/circulation/loans',
                              key='loans',
                              query=search_query)

    # trims patron ID to acceptable length
    # NOTE: patron IDs for Truman are Banner IDs, the values obtained
    # from card swipes are "BannerID + the number of the card issued",
    # i.e. if patron number 123456789 has had a card issued 3 times, a
    # possible number extracted from their card would be "12345678903".
    # Therefore, we can (hopefully) assume that no matter what input
    # length is, we can trim the patron id to a length == ID_LENGTH
    PATRON_ID_LENGTH = 9
    patron_id = id_input.get()
    patron_id = patron_id[ : PATRON_ID_LENGTH] # gets first 9 digits of input

    # iterates through queries to find matches to patron ID
    update_status(msg='Extracting item information.')
    checked_out_items = extract_queries(queries, patron_id)
    if not checked_out_items:
        update_status(msg='No items checked out within ' \
                      f'the past 15 minutes by {patron_id}.',
                      col=SUCCESS_COL,
                      enter_state='normal')
        return
    update_status(msg=f'{checked_out_items} items detected.')

    ### PRINT RECEIPT HERE ###

    # wrap-up statements
    update_status(msg=f'Printed receipt for patron {patron_id}!',
                  col=SUCCESS_COL,
                  enter_state='normal')
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
    root.title('Loan Receipt Printing')

    # formats "splash header"
    IMAGE_ROW = 0
    IMAGE_COLUMN = 0
    IMAGE_MULTIPLIER = 0.1
    image = Image.open(resource_path(LOGO_PATH)) # opens image
    image = image.resize(size=[int(IMAGE_MULTIPLIER * length) for length in image.size])
    logo = ImageTk.PhotoImage(image) # converts image to format usable by Tkinter
    tk.Label(root, image=logo).grid(row=IMAGE_ROW,
                                    column=IMAGE_COLUMN,
                                    columnspan=100,
                                    padx=(X_WIDGET_PADDING, X_WIDGET_PADDING))

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
    config_relpath = tk.Entry(root, width=INPUT_WIDTH)
    config_relpath.grid(sticky='E',
                        row=CONFIG_ROW,
                        column=CONFIG_COLUMN + 1,
                        columnspan=BUTTON_COUNT,
                        padx=INPUT_SIDE_PADDING)
    config_relpath.insert(0, DEFAULT_CONFIG_NAME) # default value

    # requests patron ID card information
    ID_ROW = CONFIG_ROW + 1
    ID_COLUMN = IMAGE_COLUMN
    id_txt = tk.Label(root,
                      text='Patron ID:\t',
                      font=FONT_TUPLE)
    id_txt.grid(sticky='W',
                row=ID_ROW,
                column=ID_COLUMN,
                padx=TEXT_SIDE_PADDING)
    id_string = tk.StringVar()
    id_input = tk.Entry(root, width=INPUT_WIDTH, textvariable=id_string)
    id_input.grid(sticky='E',
                  row=ID_ROW,
                  column=ID_COLUMN + 1,
                  columnspan=BUTTON_COUNT,
                  padx=INPUT_SIDE_PADDING)
    # new error handling with increased response time
    # https://stackoverflow.com/a/51421764    
    id_string.trace_add('write', update_validation)

    # bottom rows
    BOTTOM_ROW = 100 # arbitrarily large number
    BUTTON_ROW = BOTTOM_ROW - 10
    STATUS_ROW = BUTTON_ROW - 1
    BUTTON_COLUMN_START = IMAGE_COLUMN + 1
    STATUS_FONT = ('Courier New', 11)
    status = tk.Label(root, text='', font=STATUS_FONT)
    status.grid(sticky='W',
                row=STATUS_ROW,
                column=IMAGE_COLUMN,
                columnspan=100,
                padx=TEXT_SIDE_PADDING,
                pady=(12, 12))
    # NOTE: sticky='NESW' used to fill box to fit column and row
    enter_button = tk.Button(root, text='Enter', command=start_receipt_printing)
    enter_button.grid(sticky='NESW',
                      row=BUTTON_ROW,
                      column=BUTTON_COLUMN_START)
    enter_button.config(state='disabled') # default state is disabled
    help_button = tk.Button(root, text='Info/Help', command=open_info_help)
    help_button.grid(sticky='NESW',
                     row=BUTTON_ROW,
                     column=BUTTON_COLUMN_START + 1)
    cancel_button = tk.Button(root, text='Cancel', command=root.destroy)
    cancel_button.grid(sticky='NESW',
                       row=BUTTON_ROW,
                       column=BUTTON_COLUMN_START + 2,
                       padx=(0, X_WIDGET_PADDING))
    
    # bottom credits
    description = tk.Label(root,
                           text='\nDeveloped by Technical Services ' + \
                            '& Systems, Pickler Memorial Library, ' + \
                            'Truman State University, MO, 2024\n' + \
                            'Raw ver. info.: Z2l0aHViQGphcS1sYWduaXJhYw==',
                           justify='left',
                           font=(FONT_TUPLE[0], 7))
    description.grid(sticky='W', row=BOTTOM_ROW, column=0, columnspan=100)

    root.mainloop()