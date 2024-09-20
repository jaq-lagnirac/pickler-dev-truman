# Justin Caringal, Stephen Wynn
# [PROGRAM PURPOSE]
# Project start date (for jaq): 2024-09-13
# Project end date: TBD
import tkinter as tk
import folioclient
from reportlab.pdfgen.canvas import Canvas
import os
import sys
import json

def error_msg(msg : str = 'Unknown error occured.') -> None:
    """Pops up to user and shows error -jaq
    
    A function which organizes the creation of a TKinter box
    to show error, after which the system exits and terminates
    the program
    
    Args:
        msg (str): the message the user sees
        
    Returns:
        None, terminates program
    """
    error = tk.Tk()
    error.title("Error")
    error.geometry('350x200')
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
    REQUIRED_KEYS = {'okapi_url', 'tenant', 'username', 'password'}
    if login.keys() != REQUIRED_KEYS:
        error_msg('\"config.json\" improperly set up.')

    okapi_url = login['okapi_url']
    tenant = login['tenant']
    username = login['username']
    password = login['password']
    try:
        f = folioclient.FolioClient(okapi_url, tenant, username, password)
    except:
        error_msg('Cannot connect to FolioClient')

    return f

### TESTING QUERIES ###

f = login_folioclient()
requests = f.folio_get_all(path='request-storage/requests',key='requests',query='requestType=="Page" and status=="Open - Not yet filled"',limit=200)
import pprint
for x in requests:
    
    # pprint.pprint(x)
    
    item_id = x['itemId']
    item = f.folio_get_single_object(path=f'inventory/items/{item_id}')
    # pprint.pprint(item)

    # print('\n\n')
    print(x['instance']['title'])
    print(x['searchIndex']['callNumberComponents']['callNumber'])
    print(x['searchIndex']['shelvingOrder']) ### sorting by shelving order, not displaying
    print(x['searchIndex']['pickupServicePointName'])
    print(f'{x['requester']['lastName']} {x['requester']['barcode']}')
    print(item['effectiveLocation']['name'])


    break