# Justin Caringal
# 
# [PROGRAM PURPOSE]
# 
# Project start date: 2025-02-04
# Project end date: YYYY-MM-DD

import os
import sys
import json
from datetime import datetime, timedelta, timezone
import folioclient

VARIABLE_KEYS = [
    # 'title',
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

f = login_folioclient()
if not f:
    print('NOOOOOO')
    sys.exit()

# generates 15-min timeframe for search and comparison
time_now = datetime.now(timezone.utc) # gets current UTC time
search_window = timedelta(days=1) # creates time param
timeframe_start = time_now - search_window # calculates start of search
iso_start = timeframe_start.isoformat() # converts to ISO 8601
iso_end = time_now.isoformat()
search_query = f'dueDate > \"{iso_start}\" and dueDate < \"{iso_end}\"'
queries = f.folio_get_all(path='/circulation/loans',
                            key='loans',
                            query=search_query)

print(search_query)

from pprint import pprint
for query in queries:
    try:
        print(query['returnDate'])
    except KeyError:
        print('OVERDUE')