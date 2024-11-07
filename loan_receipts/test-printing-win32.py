# Justin Caringal, Stephen Wynn
# 
# Testing grounds for accessing and interfacing with ESC/POS printers
# 
# Project start date: 2024-10-21
# Project end date: YYYY-MM-DD

import win32print
from datetime import datetime, timezone
import sys
from pprint import pp

printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 2)
for printer in printers:
    pp(printer)
    print('\n')

printer_names = [printer['pPrinterName'] for printer in printers]
print(printer_names)

now = datetime.now(timezone.utc).astimezone().strftime('%a %d %b %Y, %I:%M%p')
print(now)

printer_name = 'Star SP700 TearBar (SP712)'
handle = win32print.OpenPrinter(printer_name)

buffer = '\n' * 10
text = f'''
If this prints, that means that I was successful!
Justin Caringal, BSCS 2025
Pickler Memorial Library, Truman State University
{now}
----------++++++++++----------++++++++++----------++++++++++
123456789012345678901234567890123456789012///
{buffer}'''.encode()

# text = None
# with open('full-pipeline-test-receipt.txt', 'r') as receipt:
#     text = receipt.read() + buffer
#     text = text.encode()
# print(text)

win32print.StartDocPrinter(handle, 1, ('Hello, world!', None, None))
win32print.WritePrinter(handle, text)
win32print.EndDocPrinter(handle)

win32print.ClosePrinter(handle)