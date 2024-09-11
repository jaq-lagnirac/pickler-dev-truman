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

# test = 'bc0330b1-a709-4e51-9c6c-d20496767b62'
# instance = f.folio_get_single_object(path=f'instance-storage/instances/{test}')
# # print(instance)
# print(bool(instance['identifiers']))
# sys.exit()

testdict = {'1':1, '2':2}
if not ('3' in testdict):
    print('no 3')

# b5d2a1a1-0bef-4b37-bce8-cf54127fdef9
# 63d2c92c-8f1a-45e4-937e-85f2f52a1708
# 672b1eff-2cbd-426c-ba40-2c296346cfe4
# 3546cad8-2514-47cb-be40-e9037d4cbbdc
# c6f7faa2-820e-52be-a2ff-7c8d89b0e3bb
# 5c87b8d0-bcc5-5c40-9cd1-84d7594b2000
# d1ef34da-810a-486c-93c3-953bd7262583
# 4992a5f2-2f65-4879-a658-3f9feff151b0
# de1eab4d-eada-49fa-b111-5e0bbf4daf80
# 9afae709-6c85-41c6-8826-b22b8daa9440
# 3f7a6fec-1152-4ed3-ac52-f236429dd249
# 0673f740-237c-496d-92aa-ffa694afd772
test_instance_id = 'c6f7faa2-820e-52be-a2ff-7c8d89b0e3bb'
instance = f.folio_get_single_object(path=f'instance-storage/instances/{test_instance_id}')
print(instance)

# with open('test.json', 'w') as test:
#     json.dump(instance, test, indent=2)
#     test.write('\n')

isbn_dict = {}
for id in instance['identifiers']:
    print(f'{id['value']:<30}{id['identifierTypeId']:<40}', end='')
    identifier = f.folio_get_single_object(path=f'identifier-types/{id['identifierTypeId']}')
    print(identifier['name'])
    if identifier['name'] == 'ISBN':
        number = id['value'].split()[0]
        isbn_dict[len(number)] = number
        print(number, isbn_dict)
    # with open('idtest.json', 'a') as idtest:
    #     json.dump(identifier, idtest, indent=2)
    #     idtest.write('\n')

if 13 in isbn_dict:
    print(isbn_dict[13])
if 10 in isbn_dict:
    print(isbn_dict[10])