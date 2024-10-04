# Justin Caringal, Stephen Wynn
#
# A program to make requests to the FolioClient API on inter-library orders and
# generate a label sheet PDF in order to facilitate the easy transfer of
# requested materials between libraries
#
# Project start date (for jaq): 2024-09-13
# Project end date: TBD

### LIBRARIES / PACKAGES ###

import tkinter as tk
import os
import sys
import json
import time
import shutil
import webbrowser as wb
from typing import Generator
import folioclient
from fillpdf import fillpdfs
from pdf2image import convert_from_path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PIL import ImageTk, Image

### GLOBAL CONSTANTS/VARIABLES ###

REPO_LINK = 'https://github.com/jaq-lagnirac/'
TEMPDIR = '.tmp_mobius_labels_jaq' # temporary directory to store intermediary generated files
SUCCESS_COL = '#00dd00'
FAIL_COL = '#ff0000'
DEFAULT_COL = '#000000'
FONT_TUPLE = ('Verdana', 10)

# scope resolution for global variables extracted from config.json
# capitalized because these are essentially constants, they won't be
# manipulated by the program, only used as inputs
LIB_CODE = None
SUPPLIED_BY = None

# keys required in config.json
REQUIRED_CONFIG_KEYS = {
    'okapi_url',
    'tenant',
    'username',
    'password',
    'lib_code',
    'supplied_by'
    }

# dynamic keys for pdf generation
REQUIRED_PDF_KEYS = {
    'Title',
    'CallNumber',
    'SendTo',
    'Patron',
    'Location',
    'LibCode',
    'SuppliedBy'
    } # ShelvingOrder not required by PDF but searched for by program

### FUNCTIONS ###

def update_warning(entry : tk.Event) -> None:
    """Updates offset_warning based off of input.
    
    A function which updates a tkinter Label based off of
    the input to the offset_value Entry
    
    Args:
        entry (str): The user-inputted entry, not interacted with
    
    Returns:
        None

    https://stackoverflow.com/a/73126296
    """

    user_offset = offset_value.get()
    # if none of the following conditions are met
    if not (user_offset.isdigit() and int(user_offset) <= 7 and int(user_offset) >=0):
        offset_msg.config(text='Offset must be a number between 0-7.\n\n\n\n\n\n\n\n',
                          fg=FAIL_COL)
        enter_button.config(state='disabled') # disables button to prevent bad offset input
    else:
        # prints offset diagram on if a label will be printed 
        is_offset = lambda label : 'X' if int(user_offset) <= label else ' '
        offset_diagram = \
            f' {is_offset(0)}|{is_offset(1)}\n' + \
            '----\n' + \
            f' {is_offset(2)}|{is_offset(3)}\n' + \
            '----\n' + \
            f' {is_offset(4)}|{is_offset(5)}\n' + \
            '----\n' + \
            f' {is_offset(6)}|{is_offset(7)}\n'

        offset_msg.config(text='Valid offset. \"X\" will be printed.\n' + offset_diagram,
                          fg=SUCCESS_COL)
        enter_button.config(state='normal') # enables button to allow label generation
    root.update()
    return


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
    system exits and terminates the program
    
    Args:
        msg (str): the message the user sees
        
    Returns:
        None, terminates program
    """
    # removes temp working sub-directory
    if os.path.exists(TEMPDIR):
        shutil.rmtree(TEMPDIR)

    # displays error window
    error = tk.Toplevel()
    error.title('Error')
    tk.Label(error, text = msg).grid(row = 0, column = 1)
    button = tk.Button(error, text = 'Cancel', width=25, command = error.destroy)
    button.grid(row = 1, column = 1)
    error.mainloop()


def safe_exit(msg : str = '', col : str = DEFAULT_COL) -> None:
    """Handles safely exiting root window functionality.
    
    A function which safely stops the program and allows for 
    continued user input. Not as harsh as error_msg(), keeps
    everything relegated to the root window as opposed to a
    pop-up window.

    Execution of this function does not necessarily denote error,
    as this function is also called on a success. This is more so
    a way to handle the clean up procedures of the root window

    Args:
        msg (str): The status message to be displayed to the user
        col (str): The hex code of the msg color
    
    Returns:
        None
    """

    # deletes temporary working sub-directory
    if os.path.exists(TEMPDIR):
        shutil.rmtree(TEMPDIR)
    
    status.config(text=msg, fg=col) # displays message to user in root
    enter_button.config(state='normal') # allows for future inputs
    root.update() # refreshes root window
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

    # initializes start-up
    info_window = tk.Toplevel()
    info_window.resizable(False, False)
    info_window.title('Info/Help')

    # adds logo image
    INFO_IMAGE_MULTIPLIER = 0.9
    info_image = Image.open(resource_path('logo-black-transparent.png')) # opens image
    info_image = image.resize(size=[int(INFO_IMAGE_MULTIPLIER * length) for length in image.size])
    info_logo = ImageTk.PhotoImage(info_image) # converts image to format usable by Tkinter
    tk.Label(info_window, image=info_logo).grid(row=0, column=0, columnspan=3)

    # creates text widget
    info_textbox = tk.Text(info_window,
                           wrap='word',
                        #    height=550,
                        #    width=650,
                           font=FONT_TUPLE)
    info_textbox.grid(row=1, column=0, columnspan=3)

    # creates scrollbar
    info_scrollbar = tk.Scrollbar(info_window)
    info_scrollbar.grid(row=0, column=100, rowspan=100, sticky='NS')

    # configures text widget to use scrollbar
    info_textbox.config(yscrollcommand=info_scrollbar.set)
    info_scrollbar.config(command=info_textbox.yview)

    # adds text to text widget
    info_txt_path = resource_path('info-help-text.txt')
    info_text = None # scope resolution
    with open(info_txt_path, 'r') as file:
        info_text = file.read()
    info_textbox.insert('end', info_text) # needs to be before text disable
    info_textbox.config(state='disabled') # disables editing of help text

    # adds button to repository documentation
    repo_button = tk.Button(info_window,
                            text='More...',
                            command=lambda: wb.open(REPO_LINK, new=1))
    repo_button.grid(row=2, column=1, sticky='NESW')
    # adds button to close help window
    cancel_info_button = tk.Button(info_window,
                                   text='Cancel',
                                   command=info_window.destroy)
    cancel_info_button.grid(row=2, column=2, sticky='NESW')

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

    # connects global variables
    global LIB_CODE
    global SUPPLIED_BY

    config_name = config_relpath.get()

    # checks for existence of config.json file, notifies user if none available -jaq
    if not os.path.exists(config_name):
        error_msg(f'\"{config_name}\" not detected.')

    # Setup FOLIO variables
    login = None # scope resolution
    with open(config_name ,'r') as config:
        login = json.load(config)

    # checks to ensure config file is set up correctly -jaq
    if not REQUIRED_CONFIG_KEYS.issubset(set(login.keys())): # if required keys not in login
        error_msg(f'\"{config_name}\" improperly set up.\nPlease check keys.' + \
                  f'\nDetected keys: {set(login.keys())}' + \
                  f'\nRequired keys: {REQUIRED_CONFIG_KEYS}')

    # unpacks relevant data from config.json file
    okapi_url = login['okapi_url']
    tenant = login['tenant']
    username = login['username']
    password = login['password']
    LIB_CODE = login['lib_code']
    SUPPLIED_BY = login['supplied_by']

    # attempts FOLIO API handshake
    f = None # scope resolution
    try:
        f = folioclient.FolioClient(okapi_url, tenant, username, password)
    except Exception as e:
        error_msg(f'Cannot connect to FolioClient.\n{e}')

    return f


def extract_info_list(f : folioclient.FolioClient,
                      requests_query : Generator[str, str, None]) -> list:
    """Extracts relevant info from queries.
    
    A function which loops over the returned requests query, extracts
    the relevant info from each request, and stores it in a list of 
    dictionaries
    
    Args:
        requests_query (folioclient.generator): a non-iterable object
            containing all of the FOLIO queries
    
    Returns:
        list: Returns a list the relevant query info
    """

    info_list = [] # list of dicts to be returned
    for request in requests_query:

        # queries itemId to extract effectiveLocation of the object
        item_id = request['itemId']
        item = None # scope resolution
        try:
            item = f.folio_get_single_object(path=f'inventory/items/{item_id}')
        except Exception as e:
            error_msg(f'Error occured with itemID extraction.\n{e}') 

        # dict to store info per request
        request_info = None # scope resolution
        try:
            request_info = { # primary key = shelvingOrder, not displaying
                'Title' : request['instance']['title'],
                'CallNumber' : request['searchIndex']['callNumberComponents']['callNumber'],
                'ShelvingOrder' : request['searchIndex']['shelvingOrder'], # primary key
                'SendTo' : request['searchIndex']['pickupServicePointName'],
                'Patron' : f'{request["requester"]["lastName"]} {request["requester"]["barcode"]}',
                'Location' : item['effectiveLocation']['name'],
                'LibCode' : LIB_CODE,
                'SuppliedBy' : SUPPLIED_BY
            } # NOTE: these are identical to the PDF labels to allow for ease-of-input
        except Exception as e:
            error_msg(f'Error occured with request info dict assembly; missing fields.\n{e}')
        
        info_list.append(request_info) # adds info to list
    
    # returns sorted list; sorted based off primary key (shelvingOrder)
    return sorted(info_list, key=lambda request_info : request_info['ShelvingOrder'])


def generate_label(template_pdf : str,
                   request : dict,
                   sorting_code : int) -> bool:
    """Creates individual label png.
    
    A function which takes a template PDF and pipelines the extracted
    request into the template, saves it as a PDF, converts the 
    PDF into a PNG, then deletes the superfluous PDF
    
    Args:
        template_pdf (str): relative path to input template PDF
        request (dict): dictionary of extracted input data
        sorting_code (int): unique identifier, allows for continuation of sorting

    Returns:
        bool: Returns True if successful
    """

    # generates temporary output pdf
    tmp_output_pdf = os.path.join(TEMPDIR, f'tmp_{sorting_code}.pdf')
    fillpdfs.write_fillable_pdf(template_pdf, tmp_output_pdf, request)

    # saves temporary pdf as png, should only be one pdf page
    output_png = os.path.join(TEMPDIR, f'tmp_{sorting_code}.png') # png chosen for lossless compression
    # NOTE: Poppler installation https://stackoverflow.com/a/70095504
    POPPLER_PATH = os.path.join('Release-24.07.0-0', 'poppler-24.07.0', 'Library', 'bin')
    images = convert_from_path(tmp_output_pdf, # list of images
                               poppler_path=resource_path(POPPLER_PATH))
    images[0].save(output_png, 'PNG') # saves the first (and only) pdf page as a png

    # deletes temporary output pdf, keeps png
    if os.path.exists(tmp_output_pdf): # prevents error if something should happen to the pdf
        os.remove(tmp_output_pdf)

    return True


def generate_labels_from_list(template_pdf : str, requests_list : list) -> int:
    """Organizes PNG generation from requests.
    
    A function which takes a list of request information, inputs them into individual
    template PDFs, then converts them into PNGs in the temporary working sub-directory

    Args:
        template_pdf (str): relative path of to input template PDF
        requests_list (list): list of extracted requests from FOLIO
    
    Returns:
        int: Returns the number of items in the requests_lists to signify a success
    """

    # calculates the number of zeros to add to beginning of sorting code with zfill
    num_of_requests = len(requests_list)
    whole_number_places = len(str(num_of_requests))

    # iterates through requests to generate images in temporary directory
    for index, request in enumerate(requests_list):
        sorting_code = str(index).zfill(whole_number_places)
        generate_label(template_pdf, request, sorting_code)

    return num_of_requests


def generate_label_sheet() -> str:
    """Stitches together generated PNGs.
    
    A function which stitches together the generated PNG labels
    and generates a printable PDF to the current working directory

    Args:
        None
    
    Returns:
        int: Returns name of the label sheet
    """

    ### LOCAL CONSTANTS ###
    # desired number of outputs per page
    NUM_COLUMNS = 2
    NUM_ROWS = 4
    TOTAL_LABELS = NUM_COLUMNS * NUM_ROWS
    # size of output page
    LETTER_WIDTH = 8.5 * inch
    LETTER_HEIGHT = 11 * inch
    # calculated height and width of label based on relation to total sheet
    LABEL_WIDTH = LETTER_WIDTH / NUM_COLUMNS
    LABEL_HEIGHT = LETTER_HEIGHT / NUM_ROWS

    # unique output sheet loosely based on ISO 8601 standard
    # https://en.wikipedia.org/wiki/ISO_8601
    iso8601_timecode = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    output_sheet_name = f'{iso8601_timecode}_label_sheet.pdf'

    canvas = Canvas(output_sheet_name, pagesize=letter) # initializes blank page

    # list of filenames in temporary directory, NOT relative paths
    # already be sorted based off of sorting code and numbering system
    img_list = os.listdir(TEMPDIR)
    # user-inputted label offset, which spot to begin print job
    try:
        user_offset = int(offset_value.get())
    except Exception:
        # most likely ValueError due to bad offset input,
        # should be prevented with button-locking
        # safely defaults to zero in case lock doesn't work
        # but will most likely never execute due to button-locking
        user_offset = 0

    # iterates through list of images
    for index, img in enumerate(img_list):
        
        img = os.path.join(TEMPDIR, img) # generates the relative path of the specific image

        # calculates page positions and offsets for each individual label
        page_position = (index + user_offset) % TOTAL_LABELS # 8 positions on the page
        x_offset = page_position % NUM_COLUMNS # left or right, which of the columns
        y_offset = page_position // NUM_COLUMNS # integer division, which of the rows
        
        # draws label img onto page
        canvas.drawImage(img,
                        x=LABEL_WIDTH * x_offset, # inputs labels left-to-right
                        y=LETTER_HEIGHT - (LABEL_HEIGHT * (1 + y_offset)), # inputs labels top-down
                        width=LABEL_WIDTH,
                        height=LABEL_HEIGHT)
        
        # prevents overlap, >= used to catch rare (hopefully impossible) exceptions
        if page_position >= (TOTAL_LABELS - 1):
            canvas.showPage() # moves on to next page

    # saves file and opens file to PDF viewer
    canvas.save()
    os.startfile(output_sheet_name)

    return output_sheet_name



def start_label_generation() -> None:
    """The response to clicking the Enter button.
    
    A function which validates the user inputs,
    organizes the login actions to FolioClient,
    and handles the label sheet PDF generation.

    Serves as the "main" function after Enter is clicked.
    
    Args:
        None
    
    Returns:
        None
    """

    # prevents future inputs
    enter_button.config(state='disabled')

    # checks to see if template pdf file exists
    template_pdf_path = template_relpath.get()
    if not os.path.exists(template_pdf_path):
        error_msg(f'\"{template_pdf_path}\" not detected.')
        safe_exit()
    # checks to make sure template has all valid keys
    template_keys = fillpdfs.get_form_fields(template_pdf_path)
    if not REQUIRED_PDF_KEYS.issubset(set(template_keys.keys())):
        error_msg(f'{template_pdf_path} does not have required keys.' + \
                  f'\nDetected keys: {set(template_keys.keys())}' + \
                  f'\nRequired keys: {REQUIRED_PDF_KEYS}')
        safe_exit()

    f = login_folioclient() # config.json validation, generates FolioClient object

    # extra insurance that user first connects to FolioClient before beginning queries
    if not f:
        safe_exit(msg='Unable to connect to FolioClient, try again.', col=FAIL_COL)
        return

    # querying FOLIOClient API
    requests_query = f.folio_get_all(path='request-storage/requests',
                                     key='requests',
                                     query='requestType==\"Page\" and status==\"Open - Not yet filled\"',
                                     limit=200)

    # extracting relevant info from requests_query
    requests_list = extract_info_list(f, requests_query)
    # requests_list = [{
    # 'Title' : 'Title',
    # 'CallNumber' : 'CallNumber',
    # 'SendTo' : 'SendTo',
    # 'Patron' : 'Patron',
    # 'Location' : 'Location',
    # 'LibCode' : 'LibCode',
    # 'SuppliedBy' : 'SuppliedBy'
    # }] # temp test data when no requests are in FOLIO
    if not requests_list: # if requests_list is empty
        safe_exit(msg='No active requests detected.', col=SUCCESS_COL)
        return
    
    # if temporary working sub-directory exists, clean
    # it out afterwards (in either case), create a new
    # empty temporary working sub-directory
    if os.path.exists(TEMPDIR):
        shutil.rmtree(TEMPDIR)
    os.makedirs(TEMPDIR)

    # generate images from requests list information
    status.config(text='Generating labels from list.', fg=DEFAULT_COL)
    root.update()
    num_images = generate_labels_from_list(template_pdf_path, requests_list)
    if not num_images:
        safe_exit(msg='Image generation not successful.', col=FAIL_COL)
        return

    # stitches together images into one PDF
    status.config(text='Stitching together images from image directory.', fg=DEFAULT_COL)
    root.update()
    output_sheet_name = generate_label_sheet()
    if not output_sheet_name:
        safe_exit(msg='Label stitching not successful.', col=FAIL_COL)
        return

    # end message on success
    plural_s = lambda : 's' if num_images != 1 else ''
    success_status = f'Successfully created {output_sheet_name} ' + \
        f'with {num_images} label{plural_s()}.'
    safe_exit(msg=success_status, col=SUCCESS_COL)
    return


# main loop functionality, generates root tkinter window where most of the user interacts
if __name__ == '__main__':
    BUTTON_COUNT = 3
    INPUT_WIDTH = 75
    IMAGE_MULTIPLIER = 0.2
    DEFAULT_TEMPLATE_NAME = os.path.join(os.getcwd(), 'mobius_label.pdf')
    DEFAULT_CONFIG_NAME = os.path.join(os.getcwd(), 'config.json')
    DEFAULT_OFFSET_VALUE = '0'
    
    root = tk.Tk()
    root.resizable(False, False)
    root.title('Mobius Label Generator')

    IMAGE_ROW = 0
    IMAGE_COLUMN = 0
    image = Image.open(resource_path('logo-black-transparent.png')) # opens image
    image = image.resize(size=[int(IMAGE_MULTIPLIER * length) for length in image.size])
    logo = ImageTk.PhotoImage(image) # converts image to format usable by Tkinter
    tk.Label(root, image=logo).grid(row=IMAGE_ROW, column=IMAGE_COLUMN, columnspan=100)

    # requests path of template PDF
    TEMPLATE_ROW = IMAGE_ROW + 1
    TEMPLATE_COLUMN = IMAGE_COLUMN
    template_txt = tk.Label(root, text='Path to template PDF:\t', font=FONT_TUPLE)
    template_txt.grid(sticky='W', row=TEMPLATE_ROW, column=TEMPLATE_COLUMN)
    template_relpath = tk.Entry(root, width=INPUT_WIDTH)
    template_relpath.grid(sticky='E',
                          row=TEMPLATE_ROW,
                          column=TEMPLATE_COLUMN + 1,
                          columnspan=BUTTON_COUNT)
    template_relpath.insert(0, DEFAULT_TEMPLATE_NAME) # default value

    # requests path of config.json
    CONFIG_ROW = TEMPLATE_ROW + 1
    CONFIG_COLUMN = IMAGE_COLUMN
    config_txt = tk.Label(root, text='Path to configuration file:\t', font=FONT_TUPLE)
    config_txt.grid(sticky='W', row=CONFIG_ROW, column=CONFIG_COLUMN)
    config_relpath = tk.Entry(root, width=INPUT_WIDTH)
    config_relpath.grid(sticky='E',
                        row=CONFIG_ROW,
                        column=CONFIG_COLUMN + 1,
                        columnspan=BUTTON_COUNT)
    config_relpath.insert(0, DEFAULT_CONFIG_NAME) # default value

    # requests label offset (to allow for printing on used label sheets)
    OFFSET_ROW = CONFIG_ROW + 1
    OFFSET_COLUMN = IMAGE_COLUMN
    label_offset_txt = tk.Label(root, text='Label offset value (0-7):\t', font=FONT_TUPLE)
    label_offset_txt.grid(sticky='W', row=OFFSET_ROW, column=OFFSET_COLUMN)
    offset_value = tk.Entry(root, width=INPUT_WIDTH)
    offset_value.grid(sticky='E',
                      row=OFFSET_ROW,
                      column=OFFSET_COLUMN + 1,
                      columnspan=BUTTON_COUNT)
    offset_value.insert(0, DEFAULT_OFFSET_VALUE) # default value
    # validation commands for offset
    validate_offset = lambda char : char.isdigit() and int(char) <= 7 and int(char) >= 0
    vcmd = (validate_offset, '%S')
    offset_value.config(validate='key', validatecommand=vcmd) # this line needs to be after default value
    # automatic checking every time offset is inputted
    offset_value.bind('<KeyRelease>', update_warning)
    # label which is updated live on if offset input is valid
    offset_msg = tk.Label(root, text='\n\n\n\n\n\n\n\n', font=FONT_TUPLE)
    offset_msg.grid(sticky='W', 
                    row=OFFSET_ROW + 1,
                    column=OFFSET_COLUMN,
                    columnspan=100)

    # bottom rows
    BOTTOM_ROW = 100 # arbitrarily large number
    BUTTON_ROW = BOTTOM_ROW - 10
    STATUS_ROW = BUTTON_ROW - 1
    BUTTON_COLUMN_START = IMAGE_COLUMN + 1
    status = tk.Label(root, text='', font=FONT_TUPLE)
    status.grid(sticky='W', row=STATUS_ROW, column=IMAGE_COLUMN, columnspan=100)
    # NOTE: sticky='NESW' used to fill box to fit column and row
    enter_button = tk.Button(root, text='Enter', command=start_label_generation)
    enter_button.grid(sticky='NESW', row=BUTTON_ROW, column=BUTTON_COLUMN_START)
    help_button = tk.Button(root, text='Info/Help', command=open_info_help)
    help_button.grid(sticky='NESW', row=BUTTON_ROW, column=BUTTON_COLUMN_START + 1)
    cancel_button = tk.Button(root, text='Cancel', command=root.destroy)
    cancel_button.grid(sticky='NESW', row=BUTTON_ROW, column=BUTTON_COLUMN_START + 2)

    # bottom credits
    description = tk.Label(root,
                           text='\nDeveloped by Justin Caringal, ' + \
                           'Pickler Memorial Library, Truman State University',
                           justify='left',
                           font=(FONT_TUPLE[0], 8))
    description.grid(sticky='W', row=BOTTOM_ROW, column=0, columnspan=100)

    root.mainloop()
    