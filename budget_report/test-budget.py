# Justin Caringal
# 
# Testing grounds, working on autmating and
# streamlining the monthly budget report
# 
# Project start date: 2024-12-06
# Project end date: YYYY-MM-DD

from sys import exit
import json
import folioclient

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

import pandas as pd

df = pd.read_csv('test.csv', sep=',')
print('original df')
print(df.to_string())
print(df.columns.to_list())
print(list(df['two']))

new_cols = ['two1', 'twotest', 'two2']
df[new_cols] = df['two'].str.split('\"', expand=True)
print('new df')
print(df.to_string())

selected_names = ['one'] + new_cols + ['three', 'four', 'five']
selected_cols = df[selected_names]
print(selected_cols)
new_df = selected_cols.copy()
new_df.to_csv('test-new.csv', index=False)