from PyPDF2 import PdfReader, PdfWriter
import sys

input_pdf = 'fillable_form.pdf'
reader = PdfReader(input_pdf)
page = reader.pages[0]
fields = reader.get_form_text_fields()
print(fields)

for field in fields:
    fields[field] = 'this is a test'
print(fields)

output_pdf = 'output.pdf'
writer = PdfWriter()
writer.add_page(page)
print(writer.pages[0].extract_text())

writer.update_page_form_field_values(
    writer.pages[0], fields
)

with open(output_pdf, 'wb') as outfile:
    writer.write(outfile)