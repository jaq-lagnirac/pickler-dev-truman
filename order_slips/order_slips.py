# Stephen Wynn, Justin Caringal
# A script to facilitate FolioClient calls to print out order slips
# Project start date (for jaq): 2024-09-09
# Project end date: 2024-09-13
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
if not REQUIRED_KEYS.issubset(set(login.keys())): # if required keys not in login
    error_msg('\"config.json\" improperly set up.')

okapi_url = login['okapi_url']
tenant = login['tenant']
username = login['username']
password = login['password']
try:
    f = folioclient.FolioClient(okapi_url, tenant, username, password)
except:
    error_msg('Cannot connect to FolioClient')

def fetch_material_type( material_type_id ):
    m = f.folio_get_single_object(path='material-types/' + material_type_id)
    return m['name']

def fetch_location( location_id ):
    l = f.folio_get_single_object(path='locations/' + location_id)
    return l['discoveryDisplayName']

def fetch_organization( organization_id ):
    o = f.folio_get_single_object(path='organizations-storage/organizations/' + organization_id)
    return o['name']

def fetch_isbn(instance_id : str) -> str:
    """Fetches ISBN of FOLIO instance -jaq
    
    A function which fetches the ISBN for a FOLIO line
    and handles the exceptions for when there is no ISBN
    present (i.e. with DVDs)
    
    Args:
        instance_id (str): the ID extracted from the Order Line
    
    Returns:
        str: Returns the ISBN if present, or an message otherwise
    """

    # attempts to fetch instance object,
    # returns negative message if exception encountered
    # most likely error a Client error '400 Bad Request'
    # if the instance ID is invalid
    instance = None # scope resolution
    try:
        instance = f.folio_get_single_object(path=f'instance-storage/instances/{instance_id}')
    except:
        return 'Unable to query ISBN'
    
    # checks to see if identifiers exist for instance
    # most likely to not exist for non-book items 
    # (i.e. DVDs, Blu-Ray, etc.)
    if not instance['identifiers']:
        return 'ISBN not applicable'

    # processes all identifiers to find ISBNs from other
    # identifiers (OCLC, Cancelled system control number,
    # etc.)
    isbn_dict = {}
    for id in instance['identifiers']:
        identifier_type = f.folio_get_single_object(path=f'identifier-types/{id['identifierTypeId']}')
        if identifier_type['name'] == 'ISBN':
            isbn = id['value'].split()[0] # split amongst spaces, only keeps number, removes ()
            isbn_dict[len(isbn)] = isbn # keyed by length to easily determine ISBN-13 vs ISBN-10
            # NOTE: IMPORTANT! This method will override multiple ISBNs of the same length (i.e.
            # if paperback and hardcover ISBN-13s are both listed, it will only keep the ISBN-13
            # processed last). This was determined to be okay for the use cases that this field
            # would be put under (used for look-up to confirm that the book ordered was correct)
            # but it may not be useful to your specific case

    # returns relevant ISBN information
    if 13 in isbn_dict: # if ISBN-13 was found (preferred)
        return f'ISBN: {isbn_dict[13]}'
    if 10 in isbn_dict: # if ISBN-13 wasn't found but ISBN-10 was
        return f'ISBN: {isbn_dict[10]}'
    return 'No ISBN found' # base case, neither ISBN-13 or ISBN-10 found

def wordwrap(txt : str, line_length_limit : int) -> list:
    """wraps text to multiple lines -jaq
    
    A function which breaks up a string into a list
    of strings, functionally allowing for the creation
    of a word-wrap-like effect
    
    Args:
        txt (str): The input string to be broken down
        line_length_limit (int): The characters per line limit,
            trailing spaces included; The terminal width
    
    Returns:
        list: A list of strings, broken down from the input txt
    """
    # set-up of info before the main loop of the function
    NOTES_HEADING = 'Notes: '
    txtlist = txt.split() # list of the string broken up by whitespace
    return_list = [NOTES_HEADING] # the list with a row of one, will be returned
    index = 0 # index counter to be used to traverse list

    # iterates through each word of the broken up txt stored in txtlist
    # and compares the possible future line length of the current
    # index/row against the terminal width. if the possible length
    # exceeds the terminal width, the loop sends the word currently
    # being processed to the next line and increments the index counter
    # to point to the new line
    for word in txtlist:
        spaced_string = f'{word} ' # restoring spaces to the string
        new_word_length = len(spaced_string)
        current_line_length = len(return_list[index])
        possible_length = current_line_length + new_word_length
        
        # if the possible future length does not exceed the terminal width, add
        # the word to the current line
        if possible_length <= line_length_limit:
            return_list[index] += spaced_string
        # if removing the space at the end of the new word will cause it to fit
        # onto the end of the line, do so (in essence, add on word instead of
        # spaced_string)
        elif (possible_length - 1) <= line_length_limit:
            return_list[index] += word
        # otherwise add the spaced string to a new line and increment the index
        # to point to this new line element
        else:
            return_list += [spaced_string]
            index += 1
    
    return return_list

def process_notes(wrapped_list : list) -> tuple[str, str, str, str]:
    """Splits list, processes overflow -jaq
    
    A function which breaks down the list of wrapped text
    and adds on notes if the length of the note exceeds four
    lines
    
    Args:
        wrapped_list (list): a list of strings processed by wordwrap
    Returns:
        (str, str, str, str): Returns tuple of strings representing the
            four lines of text to be processed by the system        
    """

    # ensures minimum length of wrapped list to prevent errors with
    # null elements in arrays
    while len(wrapped_list) < 4:
        wrapped_list += ['.'] # replaced empty string '' with '.' to signify correct print

    # unpacks notes into variables
    notes1 = wrapped_list[0]
    notes2 = wrapped_list[1]
    notes3 = wrapped_list[2]
    notes4 = wrapped_list[3]

    # adds notifier if there is more lines of notes than can be displayed
    NOTE_FOR_MORE = '...[MORE]'
    if len(wrapped_list) > 4:
        notes4 = f'{notes4[:-len(NOTE_FOR_MORE)]}{NOTE_FOR_MORE}'
    return (notes1, notes2, notes3, notes4)

def printPoLines( order, po ):
    
    orderFileName = "Orders_" + po + ".pdf"
    canvas = Canvas(orderFileName, pagesize=(1008.0, 612.0))
    yoffsetMultiplier = 210
    pagePos = 0

    # iterates through all orders
    for line in order:
        # print(line['id'])
        # input("Press any key")
        # print(line)
        # with open('DELETEME.json', 'a') as test:
        #     json.dump(line, test, indent=2)
        #     test.write('\n')

        yoffset = yoffsetMultiplier * pagePos # sets offset for left vs. right

        ### extracts relevant data ###

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
            cost = f'${line['cost']['poLineEstimatedPrice'] :.2f}' # rounds to 2 decimal places
        except:
            cost = "$?.00"

        try:
            fund = line['fundDistribution'][0]['code']
        except:
            fund = "unkown fund"

        try:
            # notes = line['details']['receivingNote']
            raw_notes = line['details']['receivingNote']
            MAX_TERMINAL_WIDTH = 60
            wrapped_notes = wordwrap(raw_notes, MAX_TERMINAL_WIDTH) # broken up list
            notes1, notes2, notes3, notes4 = process_notes(wrapped_notes)
        except:
            notes1 = notes2 = notes3 = notes4 = ""

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

        instance_id = line['instanceId']
        # print(f'{instance_id}\t-->\t{fetch_isbn(instance_id)}')
        isbn = fetch_isbn(instance_id)

        ### constants for ease of adjustment
        # x constants
        LEFT_SLIP_X = 45 # originally 45
        RIGHT_SLIP_X = 450 # originally 450
        # y constants
        TITLE = 160 # originally 160
        PUB = TITLE - 14 # originally 146
        OL = PUB - 21 # originally 108
        MAT_TYPE = OL - 21 # originally 76
        LOC = MAT_TYPE - 14 # originally 62
        # NOTES = LOC - 14 # originally 48
        NOTES1 = LOC - 14
        NOTES2 = NOTES1 - 14
        NOTES3 = NOTES2 - 14
        NOTES4 = NOTES3 - 14
        ISBN = 12 # originally 12
        # print(LEFT_SLIP_X, RIGHT_SLIP_X, TITLE, PUB, OL, MAT_TYPE, LOC, NOTES, ISBN)

        # formats routing slip (left side)
        canvas.setFont("Times-Roman", 12.0)
        canvas.drawString(LEFT_SLIP_X, TITLE + yoffset, title)
        canvas.drawString(LEFT_SLIP_X, PUB + yoffset, publisher + ". " + pubdate)
        canvas.drawString(LEFT_SLIP_X, OL + yoffset, orderline)
        canvas.drawString(LEFT_SLIP_X, MAT_TYPE + yoffset, material_type)
        canvas.drawString(LEFT_SLIP_X, LOC + yoffset, location)
        # canvas.drawString(LEFT_SLIP_X, NOTES + yoffset, notes)
        canvas.drawString(LEFT_SLIP_X, NOTES1 + yoffset, notes1)
        canvas.drawString(LEFT_SLIP_X, NOTES2 + yoffset, notes2)
        canvas.drawString(LEFT_SLIP_X, NOTES3 + yoffset, notes3)
        canvas.drawString(LEFT_SLIP_X, NOTES4 + yoffset, notes4)
        canvas.drawString(LEFT_SLIP_X, ISBN + yoffset, f'{isbn:<30}{cost} - {fund} - {vendor}')

        # formats record keeping slip (right side)
        canvas.drawString(RIGHT_SLIP_X, TITLE + yoffset, title)
        canvas.drawString(RIGHT_SLIP_X, PUB + yoffset, publisher + ". " + pubdate)
        canvas.drawString(RIGHT_SLIP_X, OL + yoffset, orderline)
        canvas.drawString(RIGHT_SLIP_X, MAT_TYPE + yoffset, material_type)
        canvas.drawString(RIGHT_SLIP_X, LOC + yoffset, location)
        # canvas.drawString(RIGHT_SLIP_X, NOTES + yoffset, notes)
        canvas.drawString(RIGHT_SLIP_X, NOTES1 + yoffset, notes1)
        canvas.drawString(RIGHT_SLIP_X, NOTES2 + yoffset, notes2)
        canvas.drawString(RIGHT_SLIP_X, NOTES3 + yoffset, notes3)
        canvas.drawString(RIGHT_SLIP_X, NOTES4 + yoffset, notes4)
        canvas.drawString(RIGHT_SLIP_X, ISBN + yoffset, f'{isbn:<30}{cost} - {fund} - {vendor}')

        pagePos = (pagePos + 1) % 3 # keeps three tickets max to a page
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


### GUI which pops up to the user to query them for order numbers ###
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
msgLine = tk.Label(root, text="Awaiting input.")
msgLine.grid(row = 3, column = 0)

root.mainloop()
