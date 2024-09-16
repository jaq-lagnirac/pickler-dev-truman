# from PyPDF2 import PdfReader, PdfWriter
from fillpdf import fillpdfs
# https://www.youtube.com/watch?v=TcBX2kb6g3o
# https://pypi.org/project/fillpdf/
# https://fillpdf.readthedocs.io/en/latest/
import sys

input_pdf = 'fillable_form.pdf'
# reader = PdfReader(input_pdf)
# page = reader.pages[0]
# fields = reader.get_form_text_fields()
# print(fields)

output_pdf = 'output_form.pdf'
# writer = PdfWriter()
# writer.add_page(page)
# print(writer.pages[0].extract_text())

# writer.update_page_form_field_values(
#     writer.pages[0], fields
# )

# with open(output_pdf, 'wb') as outfile:
#     writer.write(outfile)

fields = fillpdfs.get_form_fields(input_pdf)
print(fields)

for field in fields:
    fields[field] = 'this is a test'
print(fields)

fillpdfs.write_fillable_pdf(input_pdf, output_pdf, fields)