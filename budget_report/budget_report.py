# Justin Caringal
#
# A program to take an inputted budget report CSV file (generated from
# FOLIO), split up the relevant columns, and process the information within
# those columns
#
# Project start date: 2024-12-06
# Project end date: YYYY-MM-DD

### LIBRARIES / PACKAGES ###

import os
import sys
import tkinter as tk
from tkinter import filedialog
import webbrowser as wb
import pandas as pd
from PIL import ImageTk, Image


### GLOBAL CONSTANTS / VARIABLES ###

REPO_LINK = 'https://library.truman.edu'
SUCCESS_COL = '#00dd00'
FAIL_COL = '#ff0000'
DEFAULT_COL = '#000000'
FONT_TUPLE = ('Verdana', 10)
LOGO_PATH = os.path.join('images', 'logo-no-background.png')
HELP_PATH = os.path.join('texts', 'info-help-text.txt')


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

    # retrieves input file path from text field
    file_path = input_filename.get()

    # function validates to ensure file exists
    is_valid_file = None
    if os.path.exists(file_path):
        status.config(text='Valid file path.',
                      fg=SUCCESS_COL)
        enter_button.config(state='normal')
        is_valid_file = True
    else:
        status.config(text='File does not exist.',
                      fg=FAIL_COL)
        enter_button.config(state='disabled')
        is_valid_file = False

    # wrap-up statements
    root.update()
    return is_valid_file


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
    INFO_IMAGE_MULTIPLIER = 0.1
    info_image = Image.open(resource_path(LOGO_PATH)) # opens image
    info_image = info_image.resize(size=[int(INFO_IMAGE_MULTIPLIER * length) \
                                   for length in info_image.size])
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


def find_input_file() -> None:
    """Finds input file.
    
    A function which contains the handling to find the input
    file which contains the data to be manipulated.
    
    Args:
        None
    
    Returns:
        None
    """

    ACCEPTED_FILETYPES = [
        ('Comma-separated values', '*.csv'),
        # ('Microsoft Excel', '*.xlsx')
    ]

    # pulls up file explorer
    folder_path = filedialog.askopenfilename(parent=root,
                                             title='Find file - jaq',
                                             initialdir=os.curdir,
                                             defaultextension='.csv',
                                             filetypes=ACCEPTED_FILETYPES)
    
    input_filename.delete(0, 'end') # deletes previous text input
    input_filename.insert(0, folder_path) # inputs newly extracted folder path

    return


# Justin Caringal, TSU, BSCS 2025, github@jaq-lagnirac
# main loop functionality, generates root tkinter window
# where most of the user interacts
if __name__ == '__main__':
    BUTTON_COUNT = 3
    INPUT_WIDTH = 60
    WIDGET_PADDING = 20
    TEXT_SIDE_PADDING = (WIDGET_PADDING, 0)
    INPUT_SIDE_PADDING = (0, WIDGET_PADDING)
    SYMMETRICAL_PADDING = (WIDGET_PADDING, WIDGET_PADDING)

    # sets up window
    root = tk.Tk()
    root.resizable(False, False)
    root.title('Budget Report')

    # formats "splash header"
    IMAGE_ROW = 0
    IMAGE_COLUMN = 0
    IMAGE_MULTIPLIER = 0.35
    image = Image.open(resource_path(LOGO_PATH)) # opens image
    image = image.resize(size=[int(IMAGE_MULTIPLIER * length) \
                               for length in image.size])
    # converts image to format usable by Tkinter
    logo = ImageTk.PhotoImage(image)
    tk.Label(root, image=logo).grid(row=IMAGE_ROW,
                                    column=IMAGE_COLUMN,
                                    columnspan=100,
                                    padx=SYMMETRICAL_PADDING,
                                    pady=SYMMETRICAL_PADDING)
    
    # requests name of printer
    INPUT_FILE_ROW = IMAGE_ROW + 1
    INPUT_FILE_COLUMN = IMAGE_COLUMN
    input_file_txt = tk.Label(root,
                              text='Input filename:\t',
                              font=FONT_TUPLE)
    input_file_txt.grid(sticky='W',
                        row=INPUT_FILE_ROW,
                        column=INPUT_FILE_COLUMN,
                        padx=TEXT_SIDE_PADDING)
    filename_str = tk.StringVar() # https://stackoverflow.com/a/51421764
    input_filename = tk.Entry(root,
                              width=INPUT_WIDTH,
                              textvariable=filename_str)
    input_filename.grid(sticky='NESW',
                        row=INPUT_FILE_ROW,
                        column=INPUT_FILE_COLUMN + 1,
                        columnspan=BUTTON_COUNT - 1)
    # opens file explorer
    find_input_file_button = tk.Button(root,
                                       text='Find file...',
                                       command=find_input_file)
    find_input_file_button.grid(sticky='NESW',
                                row=INPUT_FILE_ROW,
                                column=INPUT_FILE_COLUMN + BUTTON_COUNT,
                                padx=INPUT_SIDE_PADDING)
    # adds formatting and logic to filename text input
    filename_str.trace_add('write', update_validation)
    
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
                             command=lambda:print('budget report function'))
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
                       padx=INPUT_SIDE_PADDING)
    
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