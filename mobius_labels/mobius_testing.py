import sys

input_pdf = 'fillable_form.pdf'
output_pdf = 'output_form.pdf'


from fillpdf import fillpdfs
# https://www.youtube.com/watch?v=TcBX2kb6g3o
# https://pypi.org/project/fillpdf/
# https://fillpdf.readthedocs.io/en/latest/
def test_fillpdf():
    fields = fillpdfs.get_form_fields(input_pdf)
    print(fields)

    for field in fields:
        fields[field] = 'this is a test'
    print(fields)

    fillpdfs.write_fillable_pdf(input_pdf, output_pdf, fields)


from PyPDF2 import PdfReader, PdfWriter
def test_pypdf2():
    reader = PdfReader(input_pdf)
    page = reader.pages[0]
    fields = reader.get_form_text_fields()

    for field in fields:
        fields[field] = 'this is a test'
    print(fields)

    writer = PdfWriter()
    writer.add_page(page)
    print(writer.pages[0].extract_text())
    writer.update_page_form_field_values(
        writer.pages[0], fields
    )

    writer.write(f'pypdf_{output_pdf}')


from pdf2image import convert_from_path
# import pymupdf
def test_pdf_to_img():
    # https://stackoverflow.com/a/70095504
    images = convert_from_path(output_pdf, poppler_path='Release-24.07.0-0\\poppler-24.07.0\\Library\\bin')
    for index, img in enumerate(images):
        img.save(f'test{index}.png', 'PNG')

    # doc = pymupdf.open('output_form.pdf')
    # for page in doc:
    #     pix = page.get_pixmap()
    #     pix.save(f'test{page.number}.png')


from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
def test_reportlab_tables():
    pass


# test_fillpdf()
# test_pypdf2()
test_pdf_to_img()