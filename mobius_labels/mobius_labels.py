# Justin Caringal, Stephen Wynn
# [PROGRAM PURPOSE]
# Project start date (for jaq): 2024-09-13
# Project end date: TBD

### LIBRARIES / PACKAGES ###

import tkinter as tk
import os
import sys
import json
import time
import shutil
from typing import Generator
import folioclient
from fillpdf import fillpdfs
from pdf2image import convert_from_path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

### GLOBAL CONSTANTS/VARIABLES ###

# scope resolution for global variables extracted from config.json
# capitalized because these are essentially constants, they won't be
# manipulated by the program, only used as inputs
LIB_CODE = None
SUPPLIED_BY = None
# test code for global vars
# LIB_CODE = 'TRUMN'
# SUPPLIED_BY = '''Pickler Memorial Library
# Truman State University
# 100 E Normal St.
# Kirksville, MO 63501'''

TEMPDIR = '.tmp_mobius_labels_jaq' # temporary directory to store intermediary generated files

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
DYNAMIC_KEYS = {
    'Title',
    'CallNumber',
    'ShelvingOrder',
    'SendTo',
    'Patron',
    'Location'
    }

### FUNCTIONS ###

def error_msg(msg : str = 'Unknown error occured.') -> None:
    """Pops up to user and shows error -jaq
    
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
    error = tk.Tk()
    error.title("Error")
    # error.geometry('350x200')
    tk.Label(error, text = msg).grid(row = 0, column = 1)
    button = tk.Button(error, text = "Cancel", width=25, command = error.destroy)
    button.grid(row = 1, column = 1)
    error.mainloop()
    sys.exit(1)


def login_folioclient() -> folioclient.FolioClient:
    """Organizes initial handshake with FOLIOClient -jaq
    
    A function which handles the possible exceptions on start-up
    and, if everything is in order, logs into the FOLIOClient API
    
    Args:
        None
    
    Returns:
        FolioClient: Returns an API object to the FOLIOClient
    """

    # connects global variables
    global LIB_CODE
    global SUPPLIED_BY

    # checks for existence of config.json file, notifies user if none available -jaq
    if not os.path.exists('config.json'):
        error_msg('\"config.json\" not detected in working directory.')

    # Setup FOLIO variables
    login = None # scope resolution
    with open('config.json' ,'r') as config:
        login = json.load(config)

    # checks to ensure config file is set up correctly -jaq
    if login.keys() != REQUIRED_CONFIG_KEYS:
        error_msg('\"config.json\" improperly set up.\nPlease check keys.')

    okapi_url = login['okapi_url']
    tenant = login['tenant']
    username = login['username']
    password = login['password']
    LIB_CODE = login['lib_code']
    SUPPLIED_BY = login['supplied_by']
    f = None # scope resolution
    try:
        f = folioclient.FolioClient(okapi_url, tenant, username, password)
    except Exception as e:
        error_msg(f'Cannot connect to FolioClient.\n{e}')

    return f


# NOTE: unsure if Generator annotated correctly
def extract_info_list(f : folioclient.FolioClient,
                      requests_query : Generator[None, str, str]) -> list:
    """Extracts relevant info from queries -jaq
    
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
                'Patron' : f'{request['requester']['lastName']} {request['requester']['barcode']}',
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
                   sorting_code : int) -> None:
    """Creates individual label png
    
    A function which takes a template PDF and pipelines the extracted
    request into the template, saves it as a PDF, converts the 
    PDF into a PNG, then deletes the superfluous PDF
    
    Args:
        template_pdf (str): relative path to input template PDF
        request (dict): dictionary of extracted input data
        sorting_code (int): unique identifier, allows for continuation of sorting

    Returns:
        None
    """

    # generates temporary output pdf
    tmp_output_pdf = os.path.join(TEMPDIR, f'{sorting_code}.pdf')
    fillpdfs.write_fillable_pdf(template_pdf, tmp_output_pdf, request)

    # saves temporary pdf as png, should only be one pdf page
    output_png = os.path.join(TEMPDIR, f'{sorting_code}.png') # png chosen for lossless compression
    images = convert_from_path(tmp_output_pdf, # list of images
                               poppler_path='Release-24.07.0-0\\poppler-24.07.0\\Library\\bin')
    images[0].save(output_png, 'PNG') # saves the first (and only) pdf page as a png

    # deletes temporary output pdf, keeps png
    if os.path.exists(tmp_output_pdf): # prevents error if something should happen to the pdf
        os.remove(tmp_output_pdf)

    return


def generate_labels_from_list(template_pdf : str, requests_list : list) -> None:
    """Organizes PNG generation from requests
    
    A function which takes a list of request information, inputs them into individual
    template PDFs, then converts them into PNGs in the temporary working sub-directory

    Args:
        template_pdf (str): relative path of to input template PDF
        requests_list (list): list of extracted requests from FOLIO
    
    Returns:
        None
    """

    # makes temporary working sub-directory
    if not os.path.exists(TEMPDIR):
        os.makedirs(TEMPDIR)

    # calculates the number of zeros to add to beginning of sorting code with zfill
    num_of_requests = len(requests_list)
    whole_number_places = len(str(num_of_requests))

    # iterates through requests to generate images in temporary directory
    for index, request in enumerate(requests_list):
        sorting_code = str(index).zfill(whole_number_places)
        generate_label(template_pdf, request, sorting_code)

    return


def generate_label_sheet() -> None:
    """Stitches together generated PNGs
    
    A function which stitches together the generated PNG labels
    and generates a printable PDF to the current working directory

    Args:
        None
    
    Returns:
        None
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

    img_list = os.listdir(TEMPDIR) # list of filenames in temporary directory, NOT relative paths
    for index, img in enumerate(img_list):
        
        img = os.path.join(TEMPDIR, img) # generates the relative path of the specific image

        # calculates page positions and offsets for each individual label
        page_position = index % TOTAL_LABELS # 8 positions on the page
        x_offset = page_position % NUM_COLUMNS # left or right, which of the columns
        y_offset = page_position // NUM_COLUMNS # integer division, which of the rows
        
        # draws label img onto page
        canvas.drawImage(img,
                        x=LABEL_WIDTH * x_offset, # inputs labels left-to-right
                        y=LETTER_HEIGHT - (LABEL_HEIGHT * (1 + y_offset)), # inputs labels top-down
                        width=LABEL_WIDTH,
                        height=LABEL_HEIGHT)
        
        if page_position >= (TOTAL_LABELS - 1): # prevents overlap, >= used to catch rare exceptions
            canvas.showPage() # moves on to next page

    # saves file and opens file to PDF viewer
    canvas.save()
    os.startfile(output_sheet_name)


def clicked() -> None:
    """The response to clicking the Enter button
    
    A function which organizes the login actions to FolioClient
    and handles the label sheet PDF generation
    
    Args:
        None
    
    Returns:
        None
    """

    f = login_folioclient() # generates FolioClient object

    # querying FOLIOClient API
    requests_query = f.folio_get_all(path='request-storage/requests',
                                     key='requests',
                                     query='requestType==\"Page\" and status==\"Open - Not yet filled\"',
                                     limit=200)

    # extracting relevant info from requests_query
    requests_list = extract_info_list(f, requests_query)
    
    import pprint
    pprint.pprint(requests_list)
    print('\n\n')
    for x in requests_list:
        print(x['ShelvingOrder'])
    print('\n\n')


def main():
    """THE MAIN FUNCTION"""
    root = tk.Tk()

    root.title('Mobius Label Generator')


if __name__ == '__main__':
    # main()
    clicked()