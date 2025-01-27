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
from pathlib import Path
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
    is_valid_file = None # scope resolution
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
    file which contains the data to be manipulated. Also will
    automatically start report generation once file is chosen.
    
    Args:
        None
    
    Returns:
        None
    """

    ACCEPTED_FILETYPES = [
        ('Comma-separated values', '*.csv'),
        # ('Microsoft Excel', '*.xlsx')
    ]

    # chooses where to open file explorer, depending on if
    # a Downloads folder is detected in the home directory
    # (possibly a Windows specific thing, but I don't think
    # anyone is running Linux at Pickler. This is also
    # specifically for Cassidy)
    initial_directory = os.curdir # defaults to location where exe is stored
    # downloads_path = os.path.join(Path.home(), 'Downloads')
    # if os.path.exists(downloads_path):
    #     initial_directory = downloads_path
    ### UNCOMMENT ABOVE CODE BEFORE PROD, COMMENTED OUT FOR TESTING

    # pulls up file explorer
    folder_path = filedialog.askopenfilename(parent=root,
                                             title='Find file - jaq',
                                             initialdir=initial_directory,
                                             defaultextension='.csv',
                                             filetypes=ACCEPTED_FILETYPES)
    
    input_filename.delete(0, 'end') # deletes previous text input
    input_filename.insert(0, folder_path) # inputs newly extracted folder path

    start_report_generation()

    return


def extract_data_from_csv(filename : str) -> pd.DataFrame:
    """Extracts columns of data.

    A function which: 
        1)  Ensures requisite data columns are present.
        2)  Once confirmed, splits up the needed columns and
            returns only the needed columns to the rest of
            the program for further processing.

    Args:
        filename (str): The path to the CSV file exported from FOLIO

    Returns:
        pd.DataFrame: Returns a DataFrame with the extracted columns,
            or an empty DataFrame if an error occurs
    """

    # checks to see if input file is formatted correctly
    raw_df = pd.read_csv(filename)

    # checks total column
    COST_COLUMN_NAME = 'Total'
    if not COST_COLUMN_NAME in raw_df.columns:
        update_status(msg=f'Column \"{COST_COLUMN_NAME}\" not detected.',
                      col=FAIL_COL,
                      enter_state='normal')
        return pd.DataFrame()
    cost_column = raw_df[COST_COLUMN_NAME]
    
    # checks long column
    COLUMN_TO_BE_SPLIT = 'Invoice line fund distributions'
    if not COLUMN_TO_BE_SPLIT in raw_df.columns:
        update_status(msg=f'Column \"{COLUMN_TO_BE_SPLIT}\" not detected.',
                      col=FAIL_COL,
                      enter_state='normal')
        return pd.DataFrame()
    
    # splits column into component parts
    update_status(msg=f'\"{COLUMN_TO_BE_SPLIT}\" found, splitting column.')
    # removes leading and trailing quotation marks
    cleaned_column = raw_df[COLUMN_TO_BE_SPLIT].str.strip('\"')
    # takes extracted column and splits along double quotes
    split_columns = cleaned_column.str.split('\"\"', expand=True)
    
    # renames indexed columns to new column names
    NEW_COLUMN_NAMES = {
        0 : 'Code',
        1 : 'Title',
        2 : 'Percentage Used',
        3 : 'Cost',
    }
    renamed_columns = None # scope resolution
    try:
        renamed_columns = split_columns.rename(columns=NEW_COLUMN_NAMES,
                                              errors='raise')
    except KeyError as e:
        update_status(msg='More columns than expected.',
                      col=FAIL_COL,
                      enter_state='normal')
        error_msg('More columns than expected.\n' \
                  f'See \"{COLUMN_TO_BE_SPLIT}\" in\n' \
                  f'\"{filename}\" to debug.\n\n{e}')
        return pd.DataFrame()

    # joins total column with split columns
    merged_df = pd.concat([renamed_columns, cost_column], axis=1)
    
    # fills NaN with empty string
    filled_df = merged_df.fillna('')
    return filled_df


def summarize_data(dataframe : pd.DataFrame) -> dict:
    """Sums together costs of titles.
    
    A function which takes the values in the Cost column and
    sums them together by the Title.
    
    Args:
        dataframe (pd.DataFrame): The extracted columns from the
            raw CSV
        
    Returns:
        dict: Returns a dictionary of Cost sums with Title as the
            keys
    """

    # initializes empty dict to which the sums will be collected
    cost_sums = {}

    # iterates through each row and sums Cost by Title
    # NOTE: you shouldn't have to check for the existence of the
    # columns because the program will have stopped before then
    # I may add in another check here if I have time or if the need
    # arises but for right now it should be relatively safe to ignore
    from decimal import Decimal # move up to top once working
    for index, row in dataframe.iterrows():
        # unpacks Title
        title = None # scope resolution
        if row['Title']: # if Title blank
            title = row['Title']
        else:
            title = 'Miscellaneous'

        try:
            # must convert to string first to preserve decimal places
            cost = Decimal(str(row['Total']))
        except:
            print('ERROR', index) # triggers at 599, blank Title and Total
        
        # adds to sum, or starts sum if not present
        if title in cost_sums.keys():
            cost_sums[title] += cost # adds to running total
        else: # title not in dictionary
            cost_sums[title] = cost # initializes key
            print(index, title) ### REMOVE TEST

        # if index == 548: ### REMOVE TEST
            # print(row)
            # print(cost_sums)
            # sys.exit()

    return cost_sums


def start_report_generation() -> None:
    """Organizes report generation.

    A function which serves as the "main" function for the primary
    purpose of the program, that being the extraction and processing
    of the data exported from FOLIO and the generation of a budget
    report from that data
    
    Args:
        None
    
    Returns:
        None
    """

    # prevents future inputs
    update_status(msg='Beginning report generation. Checking column names.',
                  enter_state='disabled')


    # validates column, then splits into separate columns
    filename = input_filename.get()
    budget_df = extract_data_from_csv(filename)
    if budget_df.empty:
        # specific message found in above function
        update_status(enter_state='normal') # ensures successive uses
        return
    
    budget_df.to_csv('debug.csv', index=True)
    
    # extracts and summarizes information into a dictionary
    cost_sums = summarize_data(budget_df)
    for key, value in cost_sums.items():
        print(f'{key:<25}{value:>10}')
    
    print(sum(cost_sums.values()))

    update_status(msg='[PLACEHOLDER: PROGRAM COMPLETE]',
                  col=SUCCESS_COL,
                  enter_state='normal')
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
    # opens file explorer, starts report generation
    find_input_file_button = tk.Button(root,
                                       text='Find file...',
                                       command=find_input_file)
    find_input_file_button.grid(sticky='NESW',
                                row=INPUT_FILE_ROW,
                                column=INPUT_FILE_COLUMN + BUTTON_COUNT,
                                padx=INPUT_SIDE_PADDING)
    # adds formatting and logic to filename text input
    filename_str.trace_add('write', update_validation)
    # adds Enter/Return in the filename input as an option to start program
    validate_and_start = lambda *_ : start_report_generation() \
        if update_validation() else None
    input_filename.bind('<Return>', validate_and_start)
    
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
                             command=start_report_generation)
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