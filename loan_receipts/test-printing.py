# Justin Caringal, Stephen Wynn
# 
# Testing grounds for accessing and interfacing with ESC/POS printers
# 
# Project start date: 2024-10-21
# Project end date: YYYY-MM-DD

# import os
# os.environ['PYUSB_DEBUG'] = 'debug'
# import usb.core
# usb.core.find()
import usb
import usb.backend.libusb1
# https://stackoverflow.com/a/58213525
# https://sourceforge.net/projects/libusb/
backend_path = 'W:\\loan_receipts\\libusb-1.0.20\\MS64\\dll\\libusb-1.0.dll'
backend = usb.backend.libusb1.get_backend(find_library=lambda x: backend_path)

import usb.core
# import usb.util

# Find all USB devices
devices = usb.core.find(find_all=True)

for device in devices:
    try:
        print(device)
        # for x in device:
        #     print(x)
    except Exception as e:
        print(f'ERROR: {e}')

# https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
# https://github.com/pyusb/pyusb/blob/master/docs/faq.rst
# https://github.com/pyusb/pyusb/issues/340


# for dev in devices:
#     try:
#         # Get the hardware ID
#         hwid = dev.serial_number
#         if hwid is None:
#             hwid = "N/A"
        
#         print(f"Device: {dev.product}, ID: {hwid}")

#     except usb.core.USBError as e:
#         print(f"Error accessing device: {e}")

print('-' * 100)

from escpos.printer import Usb

# if not found under Hardware Ids, find under Parent(?)
VENDOR_ID = 0x0519
PRODUCT_ID = 0x0001

# printer = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
# print(printer)
printer = Usb(VENDOR_ID, PRODUCT_ID)
printer.text('Hello, world!\n')
printer.text('It\'s Justin Caringal, @jaq_lagnirac\n')
printer.cut()

# with Usb(VENDOR_ID, PRODUCT_ID) as printer:
#     printer.text('Hello, world!\n')
#     printer.text('It\'s Justin Caringal, @jaq_lagnirac\n')