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
# lib_code = None
# supplied_by = None
# test code for global vars
lib_code = 'TRUMN'
supplied_by = '''Pickler Memorial Library
Truman State University
100 E Normal St.
Kirksville, MO 63501'''

TEMPDIR = '.tmp' # temporary directory to store intermediary generated files

# keys required in config.json
REQUIRED_CONFIG_KEYS = {
    'okapi_url',
    'tenant',
    'username',
    'password'
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
                'Location' : item['effectiveLocation']['name']
            } # NOTE: these are identical to the PDF labels to allow for ease-of-input
        except Exception as e:
            error_msg(f'Error occured with request info dict assembly; missing fields.\n{e}')
        
        info_list.append(request_info) # adds info to list
    
    # returns sorted list; sorted based off primary key (shelvingOrder)
    return sorted(info_list, key=lambda request_info : request_info['ShelvingOrder'])


def generate_label(template_pdf : str,
                   request : dict,
                   index : int) -> None:
    """placeholder description"""
    output_pdf = os.path.join(TEMPDIR, f'{index}.pdf')
    # TODO: NEED TO ADD ON LIBCODE AND SUPPLIEDBY TO REQUEST DICT
    fillpdfs.write_fillable_pdf(template_pdf, output_pdf, request)


def generate_label_sheet(request_list : list) -> None:
    """placeholder description"""

    iso8601_timecode = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    sheet_name = f'{iso8601_timecode}_label_sheet.pdf'
    if not os.path.exists(TEMPDIR):
        os.makedirs(TEMPDIR)
    for index, request in request_list:
        pass


def main():
    """THE MAIN FUNCTION"""

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


if __name__ == '__main__':
    main()
