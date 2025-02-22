# Justin Caringal
# 
# Tests extraction and API pipeline
# 
# Project start date: 2025-02-10
# Project end date: YYYY-MM-DD

import os
import sys
import json
import folioclient

tenant = '' # global scope resolution

# keys required in config.json
REQUIRED_CONFIG_KEYS = {
    'okapi_url' : 'https://okapi-mobius.folio.ebsco.com',
    'tenant' : '[INSTITUTION ID]',
    'username' : '[USERNAME]',
    'password' : '[PASSWORD]',
    }

def login_folioclient() -> folioclient.FolioClient:
    """Organizes initial handshake with FOLIOClient.
    
    A function which handles the possible exceptions on start-up
    and, if everything is in order, logs into the FOLIOClient API.
    
    Args:
        None
    
    Returns:
        FolioClient: Returns an API object to the FOLIOClient
    """

    config_name = 'config.json'

    # Setup FOLIO variables
    login = None # scope resolution
    with open(config_name ,'r') as config:
        login = json.load(config)

    # checks to ensure config file is set up correctly
    required_key_names = set(REQUIRED_CONFIG_KEYS.keys())
    # if required keys not in login
    if not required_key_names.issubset(set(login.keys())):
        print('bad keys smh')
        return

    # unpacks relevant data from config.json file
    global tenant
    okapi_url = login['okapi_url']
    tenant = login['tenant']
    username = login['username']
    password = login['password']

    # attempts FOLIO API handshake
    f = None # scope resolution
    try:
        f = folioclient.FolioClient(okapi_url, tenant, username, password)
    except Exception as e:
        print('can\'t connect, womp womp')
        return

    return f



f = login_folioclient()
if not f:
    print('NOOOOOO')
    sys.exit()

import tkinter as tk
from tkinter import ttk
def init_progress_bar():
    pbar_window = tk.Toplevel()
    pbar_window.title('Progress Bar Test')
    pbar_window.focus_force()

    progress_bar = ttk.Progressbar(pbar_window,
                                   orient='horizontal',
                                   mode='determinate')
    progress_bar.grid(sticky='NESW',
                      row=0,
                      column=0)
    
    cancel_button = tk.Button(pbar_window,
                              text='Cancel',
                              command=pbar_window.destroy)
    cancel_button.grid(sticky='NESW',
                       row=1,
                       column=0)
    
    pbar_window.mainloop()

init_progress_bar()
print('test')
sys.exit()

from pprint import pprint

call_number = 'HQ'
search_query = f'holdings.tenantId=\"{tenant}\"' \
    f' and holdingsNormalizedCallNumbers==\"{call_number}\"' \
    ' and staffSuppress==\"false\"'

total_records = f.folio_get(path='/search/instances',
                            key='totalRecords',
                            query=search_query)

queries = f.folio_get_all(path='/search/instances',
                          key='instances',
                          query=search_query)

extracted_items = []
counter = 0
for query in queries:
    counter += 1
    title = query['title']
    items = query['items']
    for item in items:
        item_info = {
            'title' : title,
            'callNumber' : 'n/a',
            'shelvingOrder' : 'n/a' # for sorting
        }

        call_num_components = item['effectiveCallNumberComponents']
        if 'callNumber' in call_num_components:
            item_info['callNumber'] = call_num_components['callNumber']

        if 'effectiveShelvingOrder' in item:
            item_info['shelvingOrder'] = item['effectiveShelvingOrder']
            extracted_items.append(item_info)

print('finished extracting')
# pprint(extracted_items)
# print('-' * 100)
sorting_reqs = lambda info : (info['shelvingOrder'])
sorted_items = sorted(extracted_items, key=sorting_reqs)
# pprint(sorted_items)
print('finished sorting')

def remove_duplicates(items):
    seen = set()
    trimmed_items = []
    for item in items:
        hashable_tuple = tuple(sorted(item.items()))
        if hashable_tuple not in seen:
            seen.add(hashable_tuple)
            trimmed_items.append(item)
    return trimmed_items

trimmed_items = remove_duplicates(sorted_items)
print(total_records, counter, len(sorted_items), len(trimmed_items))
with open('test-trimmed-call-nums.txt', 'w', encoding='utf-8') as output:
    for item in trimmed_items:
        output.write(f'{item['callNumber']}\n')

def extract_class_letters(call_number):
    letters = ""
    for char in call_number:
        if not char.isalpha():
            break
        letters += char
    return letters

print(extract_class_letters('PC 44640 C35 41978 11'))
print(extract_class_letters('PC4640 C35 1978'))