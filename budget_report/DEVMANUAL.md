# Developer Manual - Folio Budget Report

<div align="center">
    <img src="images_not_bundled/fbr-logo-color-modified.png"
    width="400px"
    alt="Budget Report Logo by github@jaq-lagnirac">
</div>

Welcome to the Development and Maintenance Manual of Folio Budget Report.
This document aims to provide a starting point for future developers of this
project as well as provide a documentation overview of the project as a whole.

If you have any questions, comments, or concerns, plese feel free to reach
out to the [Pickler Memorial Library](https://library.truman.edu)
or the current maintainers of this project.

## Table of Contents

1. [Purpose](#purpose)
1. [Project Directory Breakdown](#project-directory-breakdown)
1. [Python Dependencies](#python-dependencies)
    - [Standard Library Dependencies](#standard-library-dependencies)
    - [External Dependencies](#external-dependencies)
        - [PyInstaller](#pyinstaller)
1. [Credits and Closing](#credits-and-closing)
1. [Timestamp Details](#timestamp-details)

## Purpose

This program is intended to take the invoice data exported from the FOLIO
desktop client in the form of a CSV file, extract the relevant columns of
information, and process the data in order to generate a monthly XLSX budget
report for the library. It does not directly interface with the FOLIO client
API; rather, it takes the raw data exported from FOLIO and processes it
locally.

## Project Directory Breakdown

The following is a breakdown of the relevant files and directories present
at the time of writing.

- `images/` - A directory of images to be bundled and displayed within the
    executable.
- `images_not_bundled/` - A directory of images that will not be bundled with
    the executable.
- `testing/` - Various test PY files and TXT outputs documenting the various
    iterations of the program during initial development.
- `texts/` - A directory of texts to be bundled and displayed within the
    executable.

## Python Dependencies

When working with Python, it is good practice to create a virtual development
environment in order to have a cleaner workspace and to ensure that
dependencies between projects do not overlap or conflict during development.

Please follow the offical guide on how to create Python virtual environments
[here](https://docs.python.org/3/library/venv.html).

Below are a list of Python dependencies currently being used in the program.
Each dependency contains a link to the documentation or associated website, a
brief description of the tool as a whole, and what the library or package is
used for in the program.

### Standard Library Dependencies

Dependencies in this section are packaged with a normal Python installation and
require no external package manager installation.

The main header link leads to the official documentation for each library.
Other relevant links can be found throughout the section.

- [os](https://docs.python.org/3/library/os.html) - A library containing
    miscellaneous operating system interfaces and functions. This library is
    used to create file path strings for processing and detect the presence of
    files and directories.
- [sys](https://docs.python.org/3/library/sys.html) - A library containing
    system-specific parameters and functions. Mainly used to assist in
    generating the absolute resource path for resources (image, text). The
    resource path in necessary when bundling the script into an executable
    using [PyInstaller](#pyinstaller).
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python's built-in
    graphical user interface (GUI) library, used to display the user's
    front-end and allow the end-user to interact with the program in a
    meaningful way without having to view the raw source code.
- [webbrowser](https://docs.python.org/3/library/webbrowser.html) - Python's
    built-in web-browser controller used to link the project repository under
    the Info/Help page.
- [pathlib](https://docs.python.org/3/library/pathlib.html) - An
    object-oriented library concerned with the navigation of filesystem paths
    for a variety of different operating systems.
- [decimal](https://docs.python.org/3/library/decimal.html) - A module
    providing quick and correct floating-point arithmetic over the in-built
    `float` datatype.
-[datetime](https://docs.python.org/3/library/datetime.html) - A built-in
    Python datatype which allows for the generation and manipulation of time.
    Used to parse UTC time from the [FolioClient](#external-dependencies) API
    and convert it to a human-readable format for the end-user on the receipt.

### External Dependencies

The dependencies in this section require additional installations, with most
using the [PIP](https://pypi.org/project/pip/) package manager which comes
installed with a normal Python installation. There is one notable exception
down below.

The main header link refers to the
[PyPi Python Package Index](https://pypi.org/) project and documentation,
other relevant and/or helpful links are bulleted underneath the main header. 

- [pandas](https://pypi.org/project/pandas/) - A popular and powerful data
    analysis toolkit for Python. Used to process the exported CSV, extract the
    relevant information, manipulate the columns, and help output the processed
    data to an XLSX file.

    Relevant link(s);
    - [First-party documentation](https://pandas.pydata.org/docs/index.html)

- [PIL/Pillow](https://pypi.org/project/pillow/) - A popular imaging library
    often used as a dependency for other libraries; often serves as a standard
    medium for working with images in Python. Used by
    [tkinter](#standard-library-dependencies) to handle image display.
- [tkcalendar](https://pypi.org/project/tkcalendar/) - A package that provides
    the Calendar widget for use with a
    [tkinter](#standard-library-dependencies) graphical user interface.
- [xlsxwriter](https://pypi.org/project/XlsxWriter/) - A Python module for
    writing XLSX files and providing full formatting options.

    Relevant link(s);
    - [First-party documentation](https://xlsxwriter.readthedocs.io/)

#### PyInstaller

[PyInstaller](https://pypi.org/project/pyinstaller/) was used to bundle the
Python script and all of its external resources and dependencies into a single
executable file for ease-of-distribution and use, removing the need for a
full Python environment to be installed on a end-user's machine for full usage.

Find the full documentation [here](https://pyinstaller.org/en/stable/), as well
as the relevant SPEC file in the project repository.

## Credits and Closing

Developed for use and further development on Windows using Python 3.12+.

Developed by [Pickler Memorial Library](https://library.truman.edu/),
[Truman State University](https://www.truman.edu/).

## Timestamp Details

- **DEVMANUAL.md originally published:** 2025-02-03, Project v1.0.0
- **DEVMANUAL.md last updated:** 2025-02-03, Project v1.0.0
- **DEVMANUAL.md version:** v1.1
- **Raw ver. info. (for tracking development):** Z2l0aHViQGphcS1sYWduaXJhYw==