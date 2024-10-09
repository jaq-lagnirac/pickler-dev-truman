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

- [tkinter](https://docs.python.org/3/library/tkinter.html) - 
- [os](https://docs.python.org/3/library/os.html) - 
- [sys](https://docs.python.org/3/library/sys.html) - 
- [json](https://docs.python.org/3/library/json.html) -
- [time](https://docs.python.org/3/library/time.html) -
- [shutil](https://docs.python.org/3/library/shutil.html) -
- [webbrowser](https://docs.python.org/3/library/webbrowser.html) -
- [typing](https://docs.python.org/3/library/typing.html) -

### External Dependencies

- [folioclient]() -
- [fillpdf]() -
- [pdf2image]() -
- [reportlab]() -
- [PIL/Pillow]() -
- [poppler]() -
