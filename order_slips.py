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

def fetch_material_type( material_type_id ):
    m = f.folio_get_single_object(path='material-types/' + material_type_id)
    return m['name']

def fetch_location( location_id ):
    l = f.folio_get_single_object(path='locations/' + location_id)
    return l['discoveryDisplayName']

def fetch_organization( organization_id ):
    o = f.folio_get_single_object(path='organizations-storage/organizations/' + organization_id)
    return o['name']

def printPoLines( order, po ):
    
    orderFileName = "Orders_" + po + ".pdf"
    canvas = Canvas(orderFileName, pagesize=(1008.0, 612.0))
    yoffsetMultiplier = 210
    pagePos = 0

    for line in order:
        # print(line['id'])
        # input("Press any key")
        # print(line)
        with open('DELETEME.json', 'a') as test:
            json.dump(line, test, indent=2)
            test.write('\n')
        

        yoffset = yoffsetMultiplier * pagePos

        id = line['id']
        ponumber = line['poLineNumber']

        try:
            edition = line['edition']
        except:
            edition = ""

        try:
            copies = line['cost']['quantityPhysical']
        except:
            copies = "1"

        try:
            cost = "$" + str(line['cost']['poLineEstimatedPrice'])
        except:
            cost = "$?.00"

        try:
            fund = line['fundDistribution'][0]['code']
        except:
            fund = "unkown fund"

        try:
            notes = line['details']['receivingNote']
        except:
            notes = ""

        try:
            publisher = line['publisher']
        except:
            publisher = "unknown pub"

        try:
            pubdate = line['publicationDate']
        except:
            pubdate = "unkown pub date"

        try:
            requester = line['requester']
        except:
            requester = ""

        try:
            title = line['titleOrPackage'][0:50]   
        except:
            title = "unkown title"

        try:
            material_type = fetch_material_type(line['physical']['materialType'])
        except:
            material_type = 'unknown mat type'

        try:
            location = fetch_location(line['locations'][0]['locationId'])
        except:
            location = 'no location'
                
        try:
            vendor = fetch_organization(line['physical']['materialSupplier'])
        except:
            vendor = 'vendor unkown'
        
        #work =  publisher + ". " + pubdate
        if copies > 1:
            copystatement = copies + "copies"
        else:
            copystatement = "1 copy"
        orderline = copystatement + "; PO# " + ponumber + "; " + requester

        # formats routing slip (left side)
        canvas.setFont("Times-Roman", 12.0)
        canvas.drawString(45, 160 + yoffset, title)
        canvas.drawString(45, 146 + yoffset, publisher + ". " + pubdate)
        canvas.drawString(45, 108 + yoffset, orderline)
        canvas.drawString(45,76 + yoffset, material_type)
        canvas.drawString(45,62 + yoffset, location)
        canvas.drawString(45,48 + yoffset, notes)
        canvas.drawString(165,12 + yoffset, cost + " - " + fund + " - " + vendor)

        # formats record keeping slip (right side)
        canvas.drawString(450, 160 + yoffset, title)
        canvas.drawString(450, 146 + yoffset, publisher + ". " + pubdate)
        canvas.drawString(450, 108 + yoffset, orderline)
        canvas.drawString(450,76 + yoffset, material_type)
        canvas.drawString(450,62 + yoffset, location)
        canvas.drawString(450,48 + yoffset, notes)
        canvas.drawString(615,12 + yoffset, cost + " - " + fund + " - " + vendor)

        pagePos = (pagePos + 1) % 3
        if pagePos == 0:
            canvas.showPage()
    
    canvas.save()
    os.startfile(orderFileName)
    return orderFileName

# Function for "Enter" button: fetch content of poEntry box and call FOLIO
def clicked():
    # Get PO number from input box
    po = poEntry.get()

    # Reset input box
    poEntry.text = ""

    # Fetch po lines from FOLIO
    poLines = f.folio_get_all(path='orders/order-lines',key='poLines',query='poLineNumber=="' + po + '-*"',limit=200)
    try:
        success = printPoLines( poLines, po )
    except:
        print("Empty poLines")
        msgLine.config(text = "No order lines were returned for " + po)
        return
    
    if success != "":
        msgLine.config(text = success + " has been printed.")


root = tk.Tk()

root.title("Order Slip Printer")
root.geometry('350x500')
tk.Label(root, text = 'Enter PO number').grid(row = 0, column = 0)
poEntry = tk.Entry(root)
poEntry.grid(row = 0, column = 1)
button = tk.Button(root, text = "Enter", width=25, command = clicked)
button.grid(row = 2, column = 0)
button = tk.Button(root, text = "Cancel", width=25, command = root.destroy)
button.grid(row = 2, column = 1)
msgLine = tk.Label(root, text="msgLINE")
msgLine.grid(row = 3, column = 0)

root.mainloop()
