import tkinter as tk
import folioclient
from reportlab.pdfgen.canvas import Canvas
import tkinter as tk
import os
import sys
import json

def error_msg(msg : str = 'Unknown error occured.') -> None:
    """Pops up to user and shows error
    
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

### SETUP AND LOGIN ###

# checks for existence of config.json file, notifies user if none available
if not os.path.exists('config.json'):
    error_msg('\"config.json\" not detected in working directory.')

# Setup FOLIO variables
login = None # scope resolution
with open('config.json' ,'r') as config:
    login = json.load(config)

# checks to ensure config file is set up correctly
REQUIRED_KEYS = {'okapi_url', 'tenant', 'username', 'password'}
if login.keys() != REQUIRED_KEYS:
    error_msg('\"config.json\" improperly set up.')

okapi_url = login['okapi_url']
tenant = login['tenant']
username = login['username']
password = login['password']
f = folioclient.FolioClient(okapi_url, tenant, username, password)


### TESTING GROUNDS ###

# test_instance_id = 'bc0330b1-a709-4e51-9c6c-d20496767b62'
test_instance_id = 'b5d2a1a1-0bef-4b37-bce8-cf54127fdef9'
instance = f.folio_get_single_object(path=f'instance-storage/instances/{test_instance_id}')
print(instance)

with open('test.json', 'w') as test:
    json.dump(instance, test, indent=2)
    test.write('\n')

for id in instance['identifiers']:
    print(f'{id['value']:<30}{id['identifierTypeId']:<40}', end='')
    identifier = f.folio_get_single_object(path=f'identifier-types/{id['identifierTypeId']}')
    print(identifier['name'])
    with open('idtest.json', 'a') as idtest:
        json.dump(identifier, idtest, indent=2)
        idtest.write('\n')
