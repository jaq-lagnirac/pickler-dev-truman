# Justin Caringal, Stephen Wynn
# 
# A program to that generates and prints out the receipts for
# library patrons. Intended for Pickler Memorial Library interal
# use, may be eventually extended to outside use.
# 
# Project start date: 2024-10-21
# Project end date: 2024-11-12
# (initial delivery before comprehensive testing)

### LIBRARIES / PACKAGES ###

import os
import sys
import json
import tkinter as tk
import webbrowser as wb
from datetime import datetime, timezone, timedelta
from time import sleep
from typing import Generator
from contextlib import contextmanager
import folioclient
import win32print
from PIL import ImageTk, Image

### GLOBAL CONSTANTS / VARIABLES ###

REPO_LINK = 'https://library.truman.edu'
SUCCESS_COL = '#00dd00'
FAIL_COL = '#ff0000'
DEFAULT_COL = '#000000'
FONT_TUPLE = ('Verdana', 10)
LOGO_PATH = os.path.join('images', 'logo-no-background.png')
HELP_PATH = os.path.join('texts', 'info-help-text.txt')
SEARCH_WIN_SIZE = 100000 # minutes

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
    tk.Label(error, text=msg, justify='left').grid(row = 0, column = 1)
    error_cancel = tk.Button(error,
                             text='Cancel',
                             width=25,
                             command=error.destroy)
    error_cancel.grid(row=1, column=1)
    error.mainloop()


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

    # retrieves patron id from text field
    patron_id = id_input.get()

    # function validates to ensure patron_id contains only numbers
    is_valid_id = None
    if patron_id.isdigit():
        status.config(text='Valid Patron ID.',
                      fg=SUCCESS_COL)
        enter_button.config(state='normal')
        is_valid_id = True
    else:
        status.config(text='Patron ID must be a numerical value.',
                      fg=FAIL_COL)
        enter_button.config(state='disabled')
        is_valid_id = False

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


def find_printers() -> str:
    """Finds a list of printers.
    
    A function which uses the win32print to find a list of
    local printers to connect to and print receipts from.
    
    See DEFAULT_PRINTER_NAME under the main loop for the
    default name.
    
    Args:
        None
    
    Returns:
        str: Returns a formatted string of printer names
            and information from EnumPrinters.
    """

    # finds list of local printers
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL,
                                       None,
                                       2)
    
    # formats header with buffers
    PRINTER_NAME_BUFFER = 35
    PORT_NAME_BUFFER = 15
    LINE_LENGTH = PRINTER_NAME_BUFFER + PORT_NAME_BUFFER
    printer_info_heading = 'List of available printers and their ports:\n\n' \
        f'{'PRINTER NAME':<{PRINTER_NAME_BUFFER}}' \
        f'{'PORT NAME':<{PORT_NAME_BUFFER}}\n'
    # adds line buffer in between headers and information
    printer_text = printer_info_heading + ('-' * LINE_LENGTH) + '\n'
    # prints extracted list of printers
    for printer in printers:
        # extracts printer information from object
        printer_name = printer['pPrinterName']
        printer_port = printer['pPortName']
        # formats information and adds it to the output text
        printer_text += f'{printer_name:<{PRINTER_NAME_BUFFER}}' \
            f'{printer_port:<{PORT_NAME_BUFFER}}\n'

    return printer_text


def find_printers_window() -> None:
    """Shows user list of local printers.

    Shows a list of possible printers that may be used.
    Printers found through find_printers() function which
    utilizes win32print EnumPrinters.
    
    Args:
        None
    
    Returns:
        None
    """

    # initializes edge alignment for textbox and cancel button
    PRINTER_X_PADDING = 20

    # initializes start-up
    printers_window = tk.Toplevel()
    printers_window.resizable(False, False)
    printers_window.title('Printers Available')

    # adds logo image
    INFO_IMAGE_MULTIPLIER = 1
    printer_image = Image.open(resource_path(LOGO_PATH)) # opens image
    printer_image = image.resize(size=[int(INFO_IMAGE_MULTIPLIER * length) \
                                    for length in image.size])
    # converts image to format usable by Tkinter
    printer_logo = ImageTk.PhotoImage(printer_image)
    tk.Label(printers_window, image=printer_logo).grid(row=0,
                                                       column=0,
                                                       columnspan=3)

    # creates text widget
    printers_textbox = tk.Text(printers_window,
                           wrap='word',
                           font=('Courier New', FONT_TUPLE[1]),
                           height=12,
                           width=52)
    printers_textbox.grid(row=1,
                          column=0,
                          columnspan=3,
                          padx=(PRINTER_X_PADDING, PRINTER_X_PADDING))

    # creates scrollbar
    printers_scrollbar = tk.Scrollbar(printers_window)
    printers_scrollbar.grid(row=0,
                            column=100,
                            rowspan=100,
                            sticky='NS')

    # configures text widget to use scrollbar
    printers_textbox.config(yscrollcommand=printers_scrollbar.set)
    printers_scrollbar.config(command=printers_textbox.yview)
    
    # adds button to close help window
    PRINTER_Y_PADDING_TUPLE = (10, 10)
    cancel_info_button = tk.Button(printers_window,
                                   text='Cancel',
                                   command=printers_window.destroy)
    cancel_info_button.grid(row=2,
                            column=2,
                            sticky='NESW',
                            padx=(0, PRINTER_X_PADDING),
                            pady=PRINTER_Y_PADDING_TUPLE)
    
    # adds text to text widget
    printers_txt = find_printers()
    # fancy printing text for some extra pizzazz
    # not at all required for proper code operation
    for char in printers_txt:
        try:
            printers_textbox.config(state='normal')
            printers_textbox.insert('end', char)
            printers_textbox.config(state='disabled')
            printers_window.update()
            sleep(0.0025)
        except tk.TclError:
            return # safely ends function in case of premature window closure
    
    printers_window.mainloop()


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
    info_image = image.resize(size=[int(INFO_IMAGE_MULTIPLIER * length) \
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


def extract_single_query(f : folioclient.FolioClient,
                         query : dict) -> dict:
    """Extracts information from a single query.
    
    A function which compares the borrower barcode against the patron
    ID and outputs a dictionary depending on if it's a match.
    
    Args:
        f (FolioClient): An API object to the FOLIOClient
        query (dict): The query to be searched against
    
    Returns:
        dict: Returns a dictionary of the extracted information
    """

    # queries item ID to get title
    loan_id = query['items'][0]['loanId']
    item = f.folio_get_single_object(path=f'/circulation/loans/{loan_id}')
    
    # extracts due date, coverts to a more human-readable format
    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    iso_due_date = datetime.fromisoformat(item['dueDate'])
    iso_due_date = iso_due_date.astimezone() # defaults to system timezone
    printable_due_date = iso_due_date.strftime('%a %d %b %Y, %I:%M%p')

    # extracting and bundling the needed item information
    item_info = {
        'title' : item['item']['title'],
        'barcode' : item['item']['barcode'],
        'dueDate' : printable_due_date,
        'callNumber' : 'n/a', # default case
    }
    # some items (for some reason) do not have a call number
    # replaces blank key with filler to prevent current
    # and future KeyError(s)
    if 'callNumber' in item['item']:
        item_info['callNumber'] = item['item']['callNumber']
    return item_info


def extract_queries(f : folioclient.FolioClient,
                    queries : Generator[str, str, None]) -> list:
    """Extracts queries from FOLIO object.
    
    A function which iterates through a FOLIO object and compares
    it against the patron ID inputted by the user. If the borrower
    barcode matches the patron ID, add an extracted info dictionary
    to a list to be returned by the function.
    
    Args:
        f (FolioClient): An API object to the FOLIOClient
        queries (Generator): A non-iterable object returned by FOLIO
    
    Returns:
        list: Returns a list of dictionaries containing item information
    """

    checked_out_items = [] # list of dicts to be returned
    for query in queries:
        item_info = extract_single_query(f, query)
        
        if item_info: # if not an empty info dictionary
            checked_out_items.append(item_info)

    return checked_out_items


def center_multiline_text(text : str, width : int) -> str:
    """Breaks down and centers multiline text

    A function which takes a multiline text input and centers
    it to a specified width using the str.center() method.

    Args:
        text (str): The text to be centered, usually enclosed
            in triple quotes
        width (int): The width to be centered on
    
    Returns:
        str: Returns the newly centered multiline string
    """
    lines = text.splitlines() # splits text by \n into a list of lines
    centered_lines = [line.center(width) for line in lines] # centers lines
    return '\n'.join(centered_lines) # rejoins lines into a single output str


def format_full_receipt(checked_out_items : list,
                        time_now : datetime) -> str:
    """Forwards operations to printer.
    
    A function which formats the extracted checkout items from
    FOLIO to the printer interface, an ESC/POS-style printer.

    Args:
        checked_out_items (list): A list of dictionaries of the
            extracted information
        time_now (datetime): The datetime object used to
            generate the start of the query window
    
    Returns:
        str: The full string to be printed
    """

    RECEIPT_TEXT_WIDTH = 42

    # defaults conversion to system timezone
    # https://docs.python.org/3/library/datetime.html#datetime.datetime.astimezone
    top_loan_date = time_now.astimezone().strftime('%a %d %b %Y, %I:%M%p')

    # generates receipt header
    num_items = len(checked_out_items)
    plural_s = lambda : 's' if num_items != 1 else ''
    receipt_header = f'''
Truman State University
Pickler Memorial Library

{top_loan_date}
{num_items} item{plural_s()} checked out
in the last {SEARCH_WIN_SIZE} mins.

    '''
    centered_header = center_multiline_text(receipt_header, RECEIPT_TEXT_WIDTH)

    # generates list of items to be printed out
    item_text = ''
    for index, item in enumerate(checked_out_items):
        item_text += f'''
ITEM {index + 1}
TITLE: {item['title'][ : RECEIPT_TEXT_WIDTH - 7]}
CALL #: {item['callNumber']}
BARCODE: {item['barcode']}
DUE DATE: {item['dueDate']}
    ''' # 'TITLE: ' is 7 characters 

    # concatenating header and formatting item list to be returned
    full_receipt_text = centered_header + item_text
    return full_receipt_text


@contextmanager
def open_printer(printer_name : str) -> Generator[any, any, any]:
    """A context manager for win32print functions.
    
    A context manager function to handle all win32print interactions
    and safely exit if needed.
    
    Args:
        printer_name (str): The name of the printer from which a 
            handle will be generated and connected.
    
    Returns:
        None
    """

    print_tuple = ('Receipt Print Job by github@jaq-lagnirac', # doc name
                   None, # output file, None means print to printer
                   None) # data type, None means default from printer driver

    # acquires handle resource
    handle = win32print.OpenPrinter(printer_name)
    try:
        win32print.StartDocPrinter(handle, 1, print_tuple)
        yield handle
        win32print.EndDocPrinter(handle)
    except Exception as e:
        printer_error = 'Error occured during printing process.'
        update_status(msg=printer_error,
                      col=FAIL_COL,
                      enter_state='normal')
        error_msg(f'{printer_error}\n{e}')
    finally:
        # releases handle resource
        win32print.ClosePrinter(handle)


def start_printing_process() -> None:
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
    update_status(msg='Beginning receipt printing. Checking printers.',
                  enter_state='disabled')
    
    # checks to see if listed printer exists
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL,
                                       None,
                                       2)
    printer_names = [printer['pPrinterName'] for printer in printers]
    inputted_printer = printer_name.get()
    inputted_printer = inputted_printer.strip() # strips whitespace from input
    if send_to_printer.get() and (inputted_printer not in printer_names):
        update_status(msg=f'\"{inputted_printer}\" is not ' \
                      'a recognized printer.',
                      col=FAIL_COL,
                      enter_state='normal')
        return

    # logs into folioclient
    update_status(msg='Logging into FOLIO.')
    f = login_folioclient()
    if not f:
        # safety net to enable enter button again,
        # more detailed status messages executed during
        # login_folioclient() execution
        update_status(enter_state='normal')
        return
    
    # generates 15-min timeframe for search and comparison
    time_now = datetime.now(timezone.utc) # gets current UTC time
    search_window = timedelta(minutes=SEARCH_WIN_SIZE) # creates time param
    timeframe_start = time_now - search_window # calculates start of search
    iso_timeframe = timeframe_start.isoformat() # converts to ISO 8601

    # trims patron ID to acceptable length (NO LONGER)
    # NOTE: patron IDs for Truman are Banner IDs, the values obtained
    # from card swipes are "BannerID + the number of the card issued",
    # i.e. if patron number 123456789 has had a card issued 3 times, a
    # possible number extracted from their card would be "12345678903".
    # Therefore, we can (hopefully) assume that no matter what input
    # length is, we can trim the patron id to a length == ID_LENGTH
    #
    # NOTE 2024-12-02: Turns out we CANNOT safely assume this---the
    # system can actually take 9-digit Banner IDs, 11-digit Patron IDs,
    # 14-digit Community Borrower IDs, and any other length ID that remains
    # in the system. tl;dr trimming the ID is superfluous
    patron_id = id_input.get()

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
    # 
    # NOTE 2025-01-21: This is just a note for future maintainers, I talked
    # with some of the FOLIO developers on Slack and as of when-I-asked-them
    # (about a month ago for a different Pickler project), and they stated that
    # CQL through the FOLIO API does not support nested queries as of this
    # moment.
    update_status(msg='Querying FOLIO API.')
    search_query = f'date > \"{iso_timeframe}\"' \
        f' and userBarcode == \"{patron_id}\"' \
        ' and action == \"Checked out\"'
    queries = f.folio_get_all(path='audit-data/circulation/logs',
                              key='logRecords',
                              query=search_query)


    # iterates through queries to find matches to patron ID
    update_status(msg='Extracting item information.')
    checked_out_items = extract_queries(f, queries)
    id_input.delete(0, 'end') # deletes patron ID from input
    # test_item = {
    #     'title' : 'Loan Receipt Prints by jaq-lagnirac',
    #     'barcode' : 'Barcode',
    #     'dueDate' : 'Due',
    #     'callNumber' : 'Call Number'
    # }
    # checked_out_items = [test_item]
    if not checked_out_items:
        update_status(msg='No items checked out within ' \
                      f'the past {SEARCH_WIN_SIZE} minutes by \"{patron_id}\".',
                      col=SUCCESS_COL,
                      enter_state='normal')
        return

    # generates receipt string
    num_items = len(checked_out_items)
    plural_s = lambda : 's' if num_items != 1 else ''
    update_status(msg=f'{num_items} item{plural_s()} detected. ' \
                      'Formatting print job.')
    BUFFER = '\n' * 10 # ensures whole receipt is above the tear bar
    receipt_text = format_full_receipt(checked_out_items, time_now) + BUFFER

    if send_to_printer.get():
        # prints to named and connected printer
        with open_printer(inputted_printer) as printer_handle:
            encoded_text = receipt_text.encode('utf-8')
            win32print.WritePrinter(printer_handle, encoded_text)
    else:
        # prints to .txt file in working directory
        iso_prefix = time_now.astimezone().strftime('%Y%m%d_%H%M%S')
        receipt_filename = f'{iso_prefix}_receipt.txt'
        with open(receipt_filename, 'w') as receipt_file:
            receipt_file.write(receipt_text)

    # wrap-up statements
    update_status(msg=f'Printed receipt for patron \"{patron_id}\"!',
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
    DEFAULT_PRINTER_NAME = 'Star SP700 TearBar (SP712)'
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
    image = image.resize(size=[int(IMAGE_MULTIPLIER * length) \
                               for length in image.size])
    # converts image to format usable by Tkinter
    logo = ImageTk.PhotoImage(image)
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
    config_relpath = tk.Entry(root,
                              width=INPUT_WIDTH)
    config_relpath.grid(sticky='NESW',
                        row=CONFIG_ROW,
                        column=CONFIG_COLUMN + 1,
                        columnspan=BUTTON_COUNT,
                        padx=INPUT_SIDE_PADDING)
    config_relpath.insert(0, DEFAULT_CONFIG_NAME) # default value

    # requests name of printer
    PRINTER_ROW = CONFIG_ROW + 1
    PRINTER_COLUMN = IMAGE_COLUMN
    printer_txt = tk.Label(root,
                           text='Printer name:\t',
                           font=FONT_TUPLE)
    printer_txt.grid(sticky='W',
                     row=PRINTER_ROW,
                     column=PRINTER_COLUMN,
                     padx=TEXT_SIDE_PADDING)
    printer_name = tk.Entry(root,
                            width=INPUT_WIDTH)
    printer_name.grid(sticky='NESW',
                      row=PRINTER_ROW,
                      column=PRINTER_COLUMN + 1,
                      columnspan=BUTTON_COUNT - 1)
    printer_name.insert(0, DEFAULT_PRINTER_NAME) # default value
    # adds window to list printer names
    find_printers_button = tk.Button(root,
                                    text='Find printers...',
                                    command=find_printers_window)
    find_printers_button.grid(sticky='NESW',
                              row=PRINTER_ROW,
                              column=PRINTER_COLUMN + BUTTON_COUNT,
                              padx=INPUT_SIDE_PADDING)
    # adds option to send to printer or working directory
    CHECKBOX_ROW = PRINTER_ROW + 1
    CHECKBOX_COLUMN = IMAGE_COLUMN + 1
    send_to_printer = tk.BooleanVar(value=True)
    true_txt = 'Send receipt to printer listed above.'
    false_txt = 'Send receipt to .TXT file in working directory.'
    # updates printer checkbox text using lambda expression
    update_checkbox = lambda : printer_checkbox.config(text=true_txt) \
        if send_to_printer.get() \
            else printer_checkbox.config(text=false_txt)
    printer_checkbox = tk.Checkbutton(root,
                                      text=true_txt,
                                      justify='left',
                                      variable=send_to_printer,
                                      font=(FONT_TUPLE[0], 8),
                                      command=update_checkbox)
    printer_checkbox.grid(sticky='NSW',
                          row=CHECKBOX_ROW,
                          column=CHECKBOX_COLUMN,
                          columnspan=BUTTON_COUNT,
                          padx=INPUT_SIDE_PADDING)

    # requests patron ID card information
    ID_ROW = CHECKBOX_ROW + 1
    ID_COLUMN = IMAGE_COLUMN
    id_txt = tk.Label(root,
                      text='Patron ID:\t',
                      font=FONT_TUPLE)
    id_txt.grid(sticky='W',
                row=ID_ROW,
                column=ID_COLUMN,
                padx=TEXT_SIDE_PADDING)
    id_string = tk.StringVar()
    id_input = tk.Entry(root,
                        width=INPUT_WIDTH,
                        textvariable=id_string)
    id_input.grid(sticky='NESW',
                  row=ID_ROW,
                  column=ID_COLUMN + 1,
                  columnspan=BUTTON_COUNT,
                  padx=INPUT_SIDE_PADDING)
    # new error handling with increased response time
    # https://stackoverflow.com/a/51421764    
    id_string.trace_add('write', update_validation)
    # adds Enter/Return in the id input as an option to start program
    validate_and_start = lambda *_ : start_printing_process() \
        if update_validation() else None
    id_input.bind('<Return>', validate_and_start)

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
    enter_button = tk.Button(root,
                             text='Enter',
                             command=start_printing_process)
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
    