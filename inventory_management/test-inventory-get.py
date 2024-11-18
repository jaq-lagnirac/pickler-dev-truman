# Justin Caringal, Stephen Wynn
# 
# [PROGRAM PURPOSE]
# 
# Project start date: 2024-11-15
# Project end date: YYYY-MM-DD

import os
import sys
import json
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import folioclient

VARIABLE_KEYS = [
    'title',
    'callNumber',
    'effectiveShelvingOrder',
    'volume',
]
ALL_INFO_KEYS = VARIABLE_KEYS + [
    'status',
    'date',
    'effectiveLocation',
]

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

from datetime import datetime

def extract_item_info(item):
    iso_date = datetime.fromisoformat(item['status']['date'])
    human_readable_date = iso_date.astimezone().strftime('%b %d %Y')
    item_info = {
        'effectiveLocation' : item['effectiveLocation']['name'],
        'status' : item['status']['name'],
        'date' : human_readable_date,
    }
    info_keys = VARIABLE_KEYS
    for key in info_keys:
        if key in item:
            item_info[key] = item[key]
        else:
            item_info[key] = '-'
    return item_info

f = login_folioclient()
if not f:
    print('NOOOOOO')
    sys.exit()

user_input = 'PN'
query = f'effectiveShelvingOrder==\"{user_input}*\"'# and effectiveLocation==\"*TRUMAN Micro Film*\"'# sortBy effectiveShelvingOrder'
print(query)
inventory = f.folio_get_all(path='/inventory/items/',
                            key='items',
                            query=query)

from pprint import pp

counter = 0
from tqdm import tqdm
item_list = []
for item in tqdm(inventory):
    # pp(item)
    # pp(item['status'])
    # pp(extract_item_info(item))
    extracted_item = extract_item_info(item)
    item_list.append(extracted_item)
    # location = item['effectiveLocation']['name']
    # print(index, '\t\t', location)
    # counter += 1
    # if item['status']['name'] == 'Checked out':
    #     pp(extract_item_info(item))
sorting_reqs = lambda info : (
    info['effectiveLocation'],
    info['effectiveShelvingOrder']
)
sorted_list = sorted(tqdm(item_list), key=sorting_reqs)

import csv
with open('test-query.csv', 'w', newline='') as csvfile:
    fieldnames = ALL_INFO_KEYS
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for item in tqdm(sorted_list):
        writer.writerow(item)

print(f'\n\n\n\nitems: {counter}')
