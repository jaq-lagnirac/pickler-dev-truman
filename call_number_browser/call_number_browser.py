# Justin Caringal
# 
# A program that takes in input call number in the system and finds 
# call numbers which preceed and succeed around an input #
# 
# Project start date: 2025-02-10
# Project end date: YYYY-MM-DD

### LIBRARIES / PACKAGES ###

import os
import sys
import json
import tkinter as tk
import webbrowser as wb
from time import sleep
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
    call_num = call_num_input.get()

    # function validates to ensure call number is inputted
    is_valid_id = None
    if call_num:
        status.config(text='',
                      fg=SUCCESS_COL)
        enter_button.config(state='normal')
        is_valid_id = True
    else:
        status.config(text='Please input an LC call number.',
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


def start_call_num_search():
    """[PLACEHOLDER]"""
    print('start_call_num_search')


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