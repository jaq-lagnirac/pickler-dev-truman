# Justin Caringal, Stephen Wynn
# 
# [PROGRAM PURPOSE]
# 
# Project start date: 2024-10-21
# Project end date: YYYY-MM-DD

import os
import sys
import json
import folioclient

# keys required in config.json
REQUIRED_CONFIG_KEYS = {
    'okapi_url',
    'tenant',
    'username',
    'password',
    }

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
    print(msg)
    sys.exit()
    # # removes temp working sub-directory
    # if os.path.exists(TEMPDIR):
    #     shutil.rmtree(TEMPDIR)

    # # displays error window
    # error = tk.Toplevel()
    # error.title('Error')
    # tk.Label(error, text = msg).grid(row = 0, column = 1)
    # button = tk.Button(error, text = 'Cancel', width=25, command = error.destroy)
    # button.grid(row = 1, column = 1)
    # error.mainloop()

def login_folioclient() -> folioclient.FolioClient:
    """Organizes initial handshake with FOLIOClient.
    
    A function which handles the possible exceptions on start-up
    and, if everything is in order, logs into the FOLIOClient API.
    
    Args:
        None
    
    Returns:
        FolioClient: Returns an API object to the FOLIOClient
    """

    # config_name = config_relpath.get()
    config_name = 'config.json'

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

    # attempts FOLIO API handshake
    f = None # scope resolution
    try:
        f = folioclient.FolioClient(okapi_url, tenant, username, password)
    except Exception as e:
        error_msg(f'Cannot connect to FolioClient.\n{e}')

    return f

f = login_folioclient()

from datetime import datetime, timezone, timedelta
# local_time_now = datetime.now().isoformat()
now = datetime.now(timezone.utc)
delta = timedelta(days=1, minutes=15)
start_time = now - delta
timeframe_start = start_time.isoformat()
timeframe_end = now.isoformat()
# print(local_time_now)
print(timeframe_start)
print(timeframe_end)
print(timeframe_start < timeframe_end)

test_query1 = f'loanDate > \"{timeframe_start}\" and loanDate < \"{timeframe_end}\" and action == \"checkedout\"'
queries = f.folio_get_all(path=f'/circulation/loans',
                          key='loans',
                          query=test_query1)

barcode_query = '000010030'

from pprint import pprint
checked_out_items = []
for query in queries:
    # pprint(query)
    barcode_borrower = query['borrower']['barcode']
    if barcode_borrower == barcode_query:

        # pprint(query['borrower'])

        # extracts due date, coverts to a more human-readable format
        iso_due_date = datetime.fromisoformat(query['dueDate'])
        printable_due_date = iso_due_date.strftime('%a %d %b %Y, %I:%M%p')
        # print(f'{query['dueDate']}\t{iso_due_date}\t{printable_due_date}')

        item = query['item']
        item_dict = {
            'title' : item['title'],
            'callNumber' : item['callNumber'],
            'barcode' : item['barcode'],
            'dueDate' : printable_due_date,
        }
        checked_out_items.append(item_dict)

pprint(checked_out_items)