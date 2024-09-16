from fillpdf import fillpdfs
# https://www.youtube.com/watch?v=TcBX2kb6g3o
# https://pypi.org/project/fillpdf/
# https://fillpdf.readthedocs.io/en/latest/
import sys

input_pdf = 'fillable_form.pdf'
output_pdf = 'output_form.pdf'

fields = fillpdfs.get_form_fields(input_pdf)
print(fields)

for field in fields:
    fields[field] = 'this is a test'
print(fields)

fillpdfs.write_fillable_pdf(input_pdf, output_pdf, fields)
