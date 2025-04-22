# Developer Manual - Call Number Browser

<div align="center">
    <img src="images/logo-no-background.png"
    width="500px"
    alt="CNB Logo by github@jaq-lagnirac">
</div>

Welcome to the Development and Maintenance Manual of Call Number Browser.
This document aims to provide a starting point for future developers of this
project as well as provide a documentation overview of the project as a whole.

If you have any questions, comments, or concerns, plese feel free to reach
out to the [Pickler Memorial Library](https://library.truman.edu)
or the current maintainers of this project.

1. [Purpose](#purpose)
1. [Project Directory Breakdown](#project-directory-breakdown)
1. [Python Dependencies](#python-dependencies)
    - [Standard Library Dependencies](#standard-library-dependencies)
    - [External Dependencies](#external-dependencies)
        - [PyInstaller](#pyinstaller)
1. [Credits and Closing](#credits-and-closing)
1. [Timestamp Details](#timestamp-details)

## Purpose

This program is intended as a way to place new call numbers in an existing
database of materials in order to better illustrate where to shelve new items
to the library. The tool is case- and whitespace-sensitive and may result in
different outputs depending on what is typed in due to the lack of an
associated shelvingOrder for the item.

## Project Directory Breakdown

The following is a breakdown of the relevant files and directories present
at the time of writing.

- `images/` - A directory of images to be bundled and displayed within the
    executable.
- `testing/` - Various test PNG and PDF outputs documenting the various
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
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python's built-in
    graphical user interface (GUI) library, used to display the user's
    front-end and allow the end-user to interact with the program in a
    meaningful way without having to view the raw source code.
- [webbrowser](https://docs.python.org/3/library/webbrowser.html) - Python's
    built-in web-browser controller used to link the project repository under
    the Info/Help page.
- [bisect](https://docs.python.org/3/library/bisect.html) - A Python module
    which provides tools to insert an element into a list while maintaining
    its sorted order, used to place the input call number into a list of
    existing call numbers.
- [time](https://docs.python.org/3/library/time.html) - Python's library for
    time accesses and conversions, used to provide delays to output to end
    user.

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
- [PIL/Pillow](https://pypi.org/project/pillow/) - A popular imaging library
    often used as a dependency for other libraries; often serves as a standard
    medium for working with images in Python.
- [pycallnumber](https://pypi.org/project/pycallnumber/) - A Python module used
    to parse, model, and manipulate most types of call number strings used in
    libraries. Mainly used to handle Library of Congress, Dewey Decimal, and
    Local Juvenile Fiction call numbers.

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

- **DEVMANUAL.md originally published:** 2025-04-22, Project v1.1.0
- **DEVMANUAL.md last updated:** 2025-04-22, Project v1.1.0
- **DEVMANUAL.md version:** v1.0
- **Raw ver. info. (for tracking development):** Z2l0aHViQGphcS1sYWduaXJhYw==