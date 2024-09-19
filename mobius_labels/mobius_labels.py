# Justin Caringal, Stephen Wynn
# [PROGRAM PURPOSE]
# Project start date (for jaq): 2024-09-13
# Project end date: TBD
import tkinter as tk
import folioclient
from reportlab.pdfgen.canvas import Canvas
import os
import sys
import json

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

# checks for existence of config.json file, notifies user if none available -jaq
if not os.path.exists('config.json'):
    error_msg('\"config.json\" not detected in working directory.')

# Setup FOLIO variables
login = None # scope resolution
with open('config.json' ,'r') as config:
    login = json.load(config)

# checks to ensure config file is set up correctly -jaq
REQUIRED_KEYS = {'okapi_url', 'tenant', 'username', 'password'}
if REQUIRED_KEYS in login.keys():
    error_msg('\"config.json\" improperly set up.')

okapi_url = login['okapi_url']
tenant = login['tenant']
username = login['username']
password = login['password']
try:
    f = folioclient.FolioClient(okapi_url, tenant, username, password)
except:
    error_msg('Cannot connect to FolioClient')