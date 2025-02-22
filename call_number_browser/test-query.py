# Justin Caringal
# 
# General testing grounds for initial querying of call numbers
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

from pprint import pprint


call_number = 'P'
search_query = f'tenantId = \"{tenant}\"' \
    f' and itemNormalizedCallNumbers = {call_number}'

total_records = f.folio_get(path='/search/instances',
                            key='totalRecords',
                            query=search_query)
print(total_records)

queries = f.folio_get(path='/search/instances',
                      key='instances',
                      query=search_query)
pprint(queries)

for query in queries:
    length = len(query['items'])
    print(length)
    if length > 1:
        pprint(query['items'])
    print('-' * 100)
