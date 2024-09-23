# Justin Caringal, Stephen Wynn
# [PROGRAM PURPOSE]
# Project start date (for jaq): 2024-09-13
# Project end date: TBD

### LIBRARIES / PACKAGES
import tkinter as tk
import folioclient
from reportlab.pdfgen.canvas import Canvas
import os
import sys
import json
from typing import Generator

### FUNCTIONS ###

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
    f = None # scope resolution
    try:
        f = folioclient.FolioClient(okapi_url, tenant, username, password)
    except:
        error_msg('Cannot connect to FolioClient')

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
        except:
            error_msg('Error occured with itemID extraction.') 

        # dict to store info per request
        request_info = None # scope resolution
        try:
            request_info = { # primary key = shelvingOrder, not displaying
                'title' : request['instance']['title'],
                'callNumber' : request['searchIndex']['callNumberComponents']['callNumber'],
                'shelvingOrder' : request['searchIndex']['shelvingOrder'], # primary key
                'sendTo' : request['searchIndex']['pickupServicePointName'],
                'patron' : f'{request['requester']['lastName']} {request['requester']['barcode']}',
                'location' : item['effectiveLocation']['name']
            }
        except:
            error_msg('Error occured with request info dict assembly; missing fields.')
        
        # adds info to list
        info_list.append(request_info)
    
    # returns sorted list; sorted based off primary key (shelvingOrder)
    return sorted(info_list, key=lambda request_info : request_info['shelvingOrder'])


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
        print(x['shelvingOrder'])
    print('\n\n')

### TESTING QUERIES ###
def test():
    f = login_folioclient()
    requests = f.folio_get_all(path='request-storage/requests',
                               key='requests',
                               query='requestType=="Page" and status=="Open - Not yet filled"',
                               limit=200)

    import pprint
    for x in requests:
        
        # pprint.pprint(x)
        # print('\n\n')

        item_id = x['itemId']
        item = f.folio_get_single_object(path=f'inventory/items/{item_id}')
        # pprint.pprint(item)
        print('\n\n')

        print(x['instance']['title'])
        print(x['searchIndex']['callNumberComponents']['callNumber'])
        print(x['searchIndex']['shelvingOrder']) ### sorting by shelving order, not displaying
        print(x['searchIndex']['pickupServicePointName'])
        print(f'{x['requester']['lastName']} {x['requester']['barcode']}')
        print(item['effectiveLocation']['name'])

        # break


if __name__ == '__main__':
    main()
    # test()