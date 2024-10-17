# \[WIP v0.0\] Developer Manual - Mobius Label Generator

<div align="center">
    <img src="images_not_bundled/logo-color-background.png" width="500px" alt="MLG Logo">
</div>

Welcome to the Development and Maintenance Manual of Mobius Label Generator.
This document aims to provide a starting point for future developers of this
project as well as provide a documentation overview of the project as a whole.

If you have any questions, comments, or concerns, plese feel free to reach
out to the [Justin Caringal](https://github.com/jaq-lagnirac), the lead
developer at the time of writing, or the current maintainers of this project.

## Table of Contents

1. [Purpose](#purpose)
1. [Project Directory Breakdown](#project-directory-breakdown)
1. [Python Dependencies](#dependencies)
    - [Standard Library Dependencies](#standard-library-dependencies)
    - [External Dependencies](#external-dependencies)
        - [PyInstaller](#pyinstaller)

## Purpose

This program is intended as an open source generator to create labels to help 
facilitate interlibrary loans within the MOBIUS Linking Libraries Consortium.
The tool takes a template PDF given by the user (created using an external
tool&mdash;such as
[LibreOffice Writer](https://www.libreoffice.org/discover/writer/)&mdash;with
standard 8.5"x11" landscape letter dimensions) and generates a label sheet PDF
for use and printing on a 4x2 sticker sheet.

## Project Directory Breakdown

The following is a breakdown of the relevant files and directories present
at the time of writing.

- `images/` - A directory of images to be bundled and displayed within the
    executable.
- `images_not_bundled/` - A directory of images that will not be bundled with
    the executable.
- `testing/` - Various test PNG and PDF outputs documenting the various
    iterations of the program during initial development.
- `texts/` - A directory of texts to be bundled and displayed within the
    executable.

## Python Dependencies

Below are a list of Python dependencies currently being used in the program.
Each dependency contains a link to the documentation or associated website, a
brief description of the tool as a whole, and what the library or package is
used for in the program.

### Standard Library Dependencies

Dependencies in this section are packaged with a normal Python installation and
require no external package manager installation.

The main header link leads to the official documentation for each library.
Other relevant links can be found throughout the section.

- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python's built-in
    graphical user interface (GUI) library, used to display the user's
    front-end and allow the end-user to interact with the program in a
    meaningful way without having to view the raw source code.
- [os](https://docs.python.org/3/library/os.html) - A library containing
    miscellaneous operating system interfaces and functions. This library is
    used to create file path strings for processing, detect the presence of
    files and directories, and create the temporary working sub-directories
    extract the list of files in a directory.
- [sys](https://docs.python.org/3/library/sys.html) - A library containing
    system-specific parameters and functions. Mainly used to assist in
    generating the absolute resource path for resources (image, text). The
    resource path in necessary when bundling the script into an executable
    using [PyInstaller](#pyinstaller).
- [json](https://docs.python.org/3/library/json.html) - Python's main way of
    encoding and decoding JavaScript Object Notation (JSON) files. Its main
    function is to unpack the `config.json` configuration file and extract the
    login information to be used with the [FolioClient](#external-dependencies)
    handshake process.
- [time](https://docs.python.org/3/library/time.html) - Python's library for
    time accesses and conversions, used to generate the unique
    [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601)-based filename for the
    generated label sheet PDF.
- [shutil](https://docs.python.org/3/library/shutil.html) - A library used for
    high-level file operations, its main use is to recursively delete the
    temporary working sub-directory hierarchy.
- [webbrowser](https://docs.python.org/3/library/webbrowser.html) - Python's
    built-in web-browser controller used to link the project repository under
    the Info/Help page.
- [typing](https://docs.python.org/3/library/typing.html) - A library used as
    support for type annotation hints, used to access the Generator type
    annotation.

### External Dependencies

The dependencies in this section require additional installations, with most
using the [PIP](https://pypi.org/project/pip/) package manager which comes
installed with a normal Python installation. There is one notable exception
down below.

The main header link refers to the
[PyPi Python Package Index](https://pypi.org/) project and documentation,
other relevant and/or helpful links are bulleted underneath the main header. 

- [folioclient](https://pypi.org/project/folioclient/) - A wrapper module to
    help manage interactions to the FOLIO Library Services Platform API.
    Handles the login processes as well as make RESTful HTTP API queries to the
    main FOLIOClient API. 
    
    Relevant link(s):
    - [FOLIOClient Github page](https://github.com/FOLIO-FSE/folioclient)
    - [List of API endpoints](https://dev.folio.org/reference/api/endpoints/)
- [fillpdf](https://pypi.org/project/fillpdf/) - A package to facilitate the
    input of information into a fillable PDF based on the text field labels
    associated with each field. This package is used to fill out the template
    PDF provided by the end-user. Basic documentation found in the PyPi
    project.
- [pdf2image](https://pypi.org/project/pdf2image/) - A wrapper module which
    converts PDF files into PIL Image objects. Converts the PDF filled out with
    the information into a PNG; requires external Poppler installation (see
    below). Basic documentation found in the PyPi project.
- [reportlab](https://pypi.org/project/reportlab/) - A library for generating
    PDFs and graphics from scratch. Used to tile the label PNGs and barcode
    SVGs to generate the final label sheet PDF.

    Relevant links(s):
    - [Documenation Website](https://docs.reportlab.com/)
    - [Documentation PDF](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [PIL/Pillow](https://pypi.org/project/pillow/) -
- [poppler](https://pypi.org/project/python-poppler/) - placeholder

    ***NOTE: NOT INSTALLED WITH PIP***

    Relevant link(s):
    - [Poppler Release downloads](https://github.com/oschwartz10612/poppler-windows/releases)
        by [github@oschwartz10612](https://github.com/oschwartz10612)
    - Poppler version used by the program
        ([Release 24.07.0-0](https://github.com/oschwartz10612/poppler-windows/releases/tag/v24.07.0-0))
- [barcode](https://pypi.org/project/python-barcode/) - 

    Relevant link(s):
    - [](https://python-barcode.readthedocs.io/en/stable/)
-[svglib](https://pypi.org/project/svglib/)

#### PyInstaller