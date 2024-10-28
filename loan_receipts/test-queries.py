# Justin Caringal, Stephen Wynn
# 
# Testing grounds for querying FOLIO API and formatting text
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

test_full_card_id = '123456789'
test_extracted_id = test_full_card_id[:-2]
# print(f'{test_full_card_id}\n{test_extracted_id}')

from datetime import datetime, timezone, timedelta
now = datetime.now(timezone.utc)
delta = timedelta(days=7, minutes=15)
cutoff_time = now - delta
timeframe_start = cutoff_time.isoformat()
# print(timeframe_start)

barcode_query = '000010030'

test_query1 = f'loanDate > \"{timeframe_start}\" and action == \"checkedout\"'
test_query2 = 'item.status.name == \"Checked out\"'
queries = f.folio_get_all(path=f'/circulation/loans',
                          key='loans',
                          query=test_query1)

# print('\n\n\n')
from pprint import pprint
checked_out_items = []
total_queries = 0
matched_queries = 0
top_loan_date = None
for query in queries:
    # pprint(query)
    # continue
    # print(query['item']['title'])
    barcode_borrower = query['borrower']['barcode']
    total_queries += 1
    if barcode_borrower == barcode_query:
        matched_queries += 1
        # pprint(query['borrower'])

        # extracts due date, coverts to a more human-readable format
        iso_due_date = datetime.fromisoformat(query['dueDate'])
        printable_due_date = iso_due_date.strftime('%a %d %b %Y, %I:%M%p')
        # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        # print(f'{query['dueDate']}\t{iso_due_date}\t{printable_due_date}')

        # extracts loan date, coverts to a more human-readable format
        iso_loan_date = datetime.fromisoformat(query['loanDate'])
        printable_loan_date = iso_loan_date.strftime('%a %d %b %Y, %I:%M%p')
        # finds most recent loan date time
        if not top_loan_date or printable_loan_date > top_loan_date:
            top_loan_date = printable_loan_date

        item = query['item']
        item_dict = {
            'title' : item['title'],
            'callNumber' : item['callNumber'],
            'barcode' : item['barcode'],
            'dueDate' : printable_due_date,
        }
        checked_out_items.append(item_dict)

# pprint(checked_out_items)

RECEIPT_TEXT_WIDTH = 50
num_items = len(checked_out_items)
plural_s = lambda : 's' if num_items != 1 else ''
RECEIPT_HEADER = f'''
Truman State University
Pickler Memorial Library

{top_loan_date}
{num_items} item{plural_s()} checked out.

'''
def center_multiline_text(text, width):
    lines = text.splitlines()
    centered_lines = [line.center(width) for line in lines]
    return '\n'.join(centered_lines)

def print_items(items, width):
    item_text = ''
    for index, item in enumerate(items):
        item_text += f'''
ITEM {index + 1}
TITLE: {item['title'][ : width - 7]}
CALL #: {item['callNumber']}
BARCODE: {item['barcode']}
DUE DATE: {item['dueDate']}
''' # 'TITLE: ' is 7 characters
    return item_text
    
receipt_text = center_multiline_text(RECEIPT_HEADER, RECEIPT_TEXT_WIDTH) + \
    print_items(checked_out_items, RECEIPT_TEXT_WIDTH)

# TEST_RECEIPT = 'Truman State University'.center(text_width) + \
#     '\n' + \
#     'Pickler Memorial Libary'.center(text_width) + \
#     '\n\n' + \
#     top_loan_date.center(text_width) + \
#     '\n' + \
#     f'{num_items} item{plural_s()} checked out.'.center(text_width) + \
#     '\n\n'

print(receipt_text)

with open('test-receipt.txt', 'w') as file:
    file.write(receipt_text)