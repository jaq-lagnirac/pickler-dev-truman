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
from decimal import Decimal
from datetime import datetime
import pandas as pd
from PIL import ImageTk, Image
from tkcalendar import Calendar
import xlsxwriter


### GLOBAL CONSTANTS / VARIABLES ###

REPO_LINK = 'https://library.truman.edu'
SUCCESS_COL = '#00dd00'
FAIL_COL = '#ff0000'
DEFAULT_COL = '#000000'
FONT_TUPLE = ('Verdana', 10)
LOGO_PATH = os.path.join('images', 'logo-no-background.png')
HELP_PATH = os.path.join('texts', 'info-help-text.txt')
CALENDAR_DATE_FORMAT = 'yyyy-mm-dd'
DATETIME_FORMAT = '%Y-%m-%d'
DATE_CUTOFF_COLUMN_NAME = 'Invoice date'


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
    _, extension = os.path.splitext(file_path)

    # function validates to ensure file exists
    is_valid_file = False # scope resolution, base case
    enter_button.config(state='disabled')
    if not os.path.exists(file_path):
        status.config(text='File does not exist.',
                      fg=FAIL_COL)
    elif extension != '.csv':
        status.config(text='File exists, but is not a CSV file.',
                      fg=FAIL_COL)
    else:
        status.config(text='Valid file path.',
                      fg=SUCCESS_COL)
        enter_button.config(state='normal')
        is_valid_file = True
        
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
    INFO_IMAGE_MULTIPLIER = 0.3
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

    # chooses where to open file explorer, depending on if
    # a Downloads folder is detected in the home directory
    # (possibly a Windows specific thing, but I don't think
    # anyone is running Linux at Pickler. This is also
    # specifically for Cassidy)
    initial_directory = os.curdir # defaults to location where exe is stored
    downloads_path = os.path.join(Path.home(), 'Downloads')
    if os.path.exists(downloads_path):
        initial_directory = downloads_path

    # pulls up file explorer
    ACCEPTED_FILETYPES = [
        ('Comma-separated values', '*.csv'),
        # ('Microsoft Excel', '*.xlsx')
    ]
    # if user closes out of filedialog prematurely, then folder_path = ''
    folder_path = filedialog.askopenfilename(parent=root,
                                             title='Find file - jaq',
                                             initialdir=initial_directory,
                                             defaultextension='.csv',
                                             filetypes=ACCEPTED_FILETYPES)
    
    input_filename.delete(0, 'end') # deletes previous text input
    input_filename.insert(0, folder_path) # inputs newly extracted folder path

    return


def column_exists(column_name : str, df : pd.DataFrame) -> bool:
    """Checks for a column's existence.
    
    A function which checks for the existence of a column
    within a Pandas DataFrame and returns a boolean value
    on if it exists and updates the status message.
    
    Args:
        column_name (str): The name of the column to check for
        df (pd.DataFrame): The dataframe in which to check
        
    Returns:
        bool: Returns True if the column exists in the dataframe,
            False otherwise
    """
    if not column_name in df.columns:
        update_status(msg=f'Column \"{column_name}\" not detected.',
                      col=FAIL_COL,
                      enter_state='normal')
        return False
    update_status(msg=f'{column_name} found.')
    return True


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
    if not column_exists(COST_COLUMN_NAME, raw_df):
        return pd.DataFrame() # prematurely returns empty df
    cost_column = raw_df[COST_COLUMN_NAME]

    # checks date column
    DATE_COLUMN_NAME = DATE_CUTOFF_COLUMN_NAME
    if not column_exists(DATE_COLUMN_NAME, raw_df):
        return pd.DataFrame() # prematurely returns empty df
    # lambda function to convert us MM/DD/YYYY to Python datetime object
    convert_us_to_dt = lambda us_date : datetime.strptime(us_date, '%m/%d/%Y')
    # applies lambda over date column
    date_column = raw_df[DATE_COLUMN_NAME].apply(convert_us_to_dt)
    
    # checks long column
    COLUMN_TO_BE_SPLIT = 'Invoice line fund distributions'
    if not column_exists(COLUMN_TO_BE_SPLIT, raw_df):
        return pd.DataFrame() # prematurely returns empty df
    
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
    merged_df = pd.concat([date_column, renamed_columns, cost_column], axis=1)
    
    # fills NaN with empty string, allows the rest of
    # the program to process exceptions and empty strings
    filled_df = merged_df.fillna('')
    return filled_df


def sum_costs(dataframe : pd.DataFrame) -> tuple[dict, dict]:
    """Sums together costs of titles.
    
    A function which takes the values in the Cost column and
    sums them together by the Title.
    
    Args:
        dataframe (pd.DataFrame): The extracted columns from the
            raw CSV
        
    Returns:
        tuple[dict, dict]: Returns two dictionaries with Cost sums
            broken down by Title, one with YTD expenditures and one
            with "current" expenditures for the past month
    """

    # initializes empty dict in which the sums will be collected
    ytd_cost_sums = {}
    current_cost_sums = {}

    # iterates through each row and sums Cost by Title
    # NOTE: you shouldn't have to check for the existence of the
    # columns because the program will have stopped before then
    # I may add in another check here if I have time or if the need
    # arises but for right now it should be relatively safe to ignore
    for _, row in dataframe.iterrows():
        
        ### UNPACKING INFORMATION

        # checks for existence of Cost
        if not row['Total']: # if no cost associated with row (i.e. empty)
            continue # then skip to next row
        # must convert to string first to preserve decimal places
        cost = Decimal(str(row['Total']))

        # unpacks Title
        title = 'Miscellaneous' # scope resolution, default case
        if row['Title']: # if Title not blank
            title = row['Title']
        
        ### YTD EXPENDITURES

        # adds to sum, or starts sum if not present
        if title in ytd_cost_sums.keys():
            ytd_cost_sums[title] += cost # adds to running total
        else: # title not in dictionary
            ytd_cost_sums[title] = cost # initializes key and value

        ### CURRENT EXPENDITURES
        
        cutoff_date = datetime.strptime(calendar.get_date(), DATETIME_FORMAT)
        # if payment date is before cutoff
        if row[DATE_CUTOFF_COLUMN_NAME] < cutoff_date:
            continue # then continue to next iteration

        # if payment date is after cutoff, proceed to the following
        if title in current_cost_sums.keys():
            current_cost_sums[title] += cost # adds to running total
        else: # title not in dictionary
            current_cost_sums[title] = cost # initializes key and value
    
    # finds complement of subset (ytd keys missing from current)
    # i.e. finds keys found in YTD costs dict and not in current costs dict
    missing_keys = set(ytd_cost_sums.keys()) - set(current_cost_sums.keys())

    # fills in missing gaps to prevent KeyError during XLSX creation
    for key in missing_keys:
        current_cost_sums[key] = 0.0

    return (ytd_cost_sums, current_cost_sums)


def generate_xlsx_report(file_path : str,
                         ytd_cost_sums : dict,
                         current_cost_sums : dict) -> str:
    """Generates budget report as an XLSX file
    
    A function which takes the summed costs from the raw file
    and formats and outputs it onto an XLSX file
    
    Args:
        file_path (str): the name of the original exported CSV
        ytd_cost_sums (str): dict containing YTD expenditures
        current_cost_sums (str): dict containing current monthly expenditures
    
    Returns:
        str: Returns the name of the output XLSX file.
    """

    # creates output filename
    filename = os.path.basename(file_path)
    basename, _ = os.path.splitext(filename)
    output_filename = f'REPORT_{basename}-jaq.xlsx'

    # initializes workbook
    workbook = xlsxwriter.Workbook(output_filename)
    worksheet = workbook.add_worksheet()

    # sets column headers
    COLUMN_NAMES = [
        'SUBFUND',
        'APPROPRIATION',
        'CURRENT EXPENDITURES',
        'YTD EXPENDITURES',
        'ENCUMBRANCES',
        'FREE BALANCE',
    ]
    COLUMN_HEADER_FORMAT = workbook.add_format(
        {
            'bold' : 1,
            'italic' : 1,    
        }
    )
    worksheet.write_row('A3',
                        COLUMN_NAMES,
                        COLUMN_HEADER_FORMAT)
    
    ### FORMATS BULK OF TABLE
    # sorts keys to be displayed in alphabetical
    # order, adds buffer to keys
    BUFFER_STR = ''
    SUMS_BUFFER_SPACES = 3
    sorted_keys = sorted(ytd_cost_sums.keys()) + \
        [BUFFER_STR] * SUMS_BUFFER_SPACES
    START_ROW = 4 # A1 notation row that cost sums start being printed on
    SUBFUND_FORMAT = workbook.add_format(
        {
            'italic' : 1,    
        }
    )
    CURRENCY_FORMAT = workbook.add_format(
        {
            'num_format' : '$#,##0.00',
        }
    )
    
    ### FILLS OUT BULK OF TABLE
    for index, subfund in enumerate(sorted_keys):

        # calculates current working row
        row = START_ROW + index

        # prevents KeyError from dicts
        current_expenditures = 0
        ytd_expenditures = 0
        if subfund != BUFFER_STR:
            current_expenditures = current_cost_sums[subfund]
            ytd_expenditures = ytd_cost_sums[subfund]

        # fills out table
        APPROPRIATION_DEFAULT = 0
        ENCUMBRANCE_DEFAULT = 0
        worksheet.write(f'A{row}',
                        subfund,
                        SUBFUND_FORMAT)
        worksheet.write(f'B{row}',
                        APPROPRIATION_DEFAULT,
                        CURRENCY_FORMAT)
        worksheet.write(f'C{row}',
                        current_expenditures,
                        CURRENCY_FORMAT)
        worksheet.write(f'D{row}',
                        ytd_expenditures,
                        CURRENCY_FORMAT)
        worksheet.write(f'E{row}',
                        ENCUMBRANCE_DEFAULT,
                        CURRENCY_FORMAT)
        # writes FREE BALANCE formula in required column
        worksheet.write_formula(f'F{row}',
                                f'=B{row}-D{row}-E{row}',
                                CURRENCY_FORMAT)
    
    ### TOTALS ROW
    # formats and prints column totals
    TOTALS_ROW = START_ROW + len(sorted_keys) # calculates sum row placement
    TOTALS_FORMAT = workbook.add_format(
        {
            'bold' : 1,
            'top' : 6, # Index: 6, Name: Double; Weight: 3; Style: =====
            'num_format' : '$#,##0.00',
        }
    )
    worksheet.write(f'A{TOTALS_ROW}',
                    'TOTALS',
                    TOTALS_FORMAT)
    TOTALS_COLUMN_NAMES = 'BCDEF'
    # TOTALS_FORMAT.set_num_format('$#,##0.00') # adds num_format to sum row
    for column in TOTALS_COLUMN_NAMES:
        totals_formula = f'=SUM({column}{START_ROW}:{column}{TOTALS_ROW - 1})'
        worksheet.write_formula(f'{column}{TOTALS_ROW}',
                                totals_formula,
                                TOTALS_FORMAT)
    
    ### ADDS CONDITIONAL FORMATTING
    currency_range = f'B{START_ROW}:F{TOTALS_ROW}'
    RED_FORMAT = workbook.add_format({'bg_color' : '#f4cccc'}) # light red 3
    GREEN_FORMAT = workbook.add_format({'bg_color' : '#d9ead3'}) # light green 3
    worksheet.conditional_format(currency_range, {'type' : 'cell',
                                                  'criteria' : 'less than',
                                                  'value' : 0,
                                                  'format' : RED_FORMAT})
    worksheet.conditional_format(currency_range, {'type' : 'cell',
                                                  'criteria' : 'greater than',
                                                  'value' : 0,
                                                  'format' : GREEN_FORMAT})
    
    worksheet.autofit() # reformats cell width


    # sets up worksheet headers
    # NOTE:worksheet headers must come after rest of table (and
    # specifically autofit) because autofitting to a merged cell
    # is wonky and doesn't really work, at least under my current
    # understanding of how the autofit function works
    HEADER_TEXT = f'REPORT - CUTOFF DATE: {calendar.get_date()}'
    HEADER_FORMAT = workbook.add_format(
        {
            'bold' : 1,
            'align' : 'center',
            'bottom' : 6, # Index: 6, Name: Double; Weight: 3; Style: =====
        }
    )
    worksheet.merge_range('A1:F1', '', HEADER_FORMAT)
    worksheet.merge_range('A2:F2', HEADER_TEXT, HEADER_FORMAT)

    workbook.close()
    return output_filename


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
        
    # extracts and summarizes information into a dictionary
    ytd_cost_sums, current_cost_sums = sum_costs(budget_df)
    # for key, value in ytd_cost_sums.items():
    #     print(f'{key:<25}{value:>10}')
    # for key, value in current_cost_sums.items():
    #     print(f'{key:<25}{value:>10}')

    # generates report for xlsx table
    output_filename = generate_xlsx_report(filename,
                                           ytd_cost_sums,
                                           current_cost_sums)

    update_status(msg=f'Generated {output_filename}.',
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
    
    # requests name of input file
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

    # requests cutoff day for expenditures
    DATE_ROW = INPUT_FILE_ROW + 1
    DATE_COLUMN = INPUT_FILE_COLUMN
    date_txt = tk.Label(root,
                        text='Cutoff date for ' \
                          '\"Current Expenditures\":',
                        font=FONT_TUPLE)
    date_txt.grid(sticky='W',
                  row=DATE_ROW,
                  column=DATE_COLUMN,
                  padx=TEXT_SIDE_PADDING)
    calendar = Calendar(root,
                        selectmode = 'day',
                        date_pattern = CALENDAR_DATE_FORMAT)
    calendar.grid(sticky='NESW',
                  row=DATE_ROW,
                  column=DATE_COLUMN + 1,
                  columnspan=1,
                  pady = (10, 0))
    
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