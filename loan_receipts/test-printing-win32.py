import win32print
from datetime import datetime, timezone

# printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 2)
# for printer in printers:
#     print(printer)

now = datetime.now(timezone.utc).astimezone().strftime('%a %d %b %Y, %I:%M%p')
print(now)

printer_name = 'Star SP700 TearBar (SP712)'
handle = win32print.OpenPrinter(printer_name)

# with open('full-pipeline-test-receipt.txt', 'r') as receipt:
text = f'''
If this prints, that means that I was successful!
Justin Caringal, BSCS 2025
Pickler Memorial Library, Truman State University
{now}
----------++++++++++----------++++++++++----------++++++++++
123456789012345678901234567890123456789012///
\n\n\n\n\n\n\n\n\n\n'''.encode()
win32print.StartDocPrinter(handle, 1, ('Hello, world!', None, None))
win32print.WritePrinter(handle, text)
win32print.EndDocPrinter(handle)

win32print.ClosePrinter(handle)