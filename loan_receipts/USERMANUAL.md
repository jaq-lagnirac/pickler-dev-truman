# User Manual - Pickler Loan Receipts

<div align="center">
    <img src="images_not_bundled/logo-color-circle.png"
    width="400px"
    alt="Loan Receipts Logo by github@jaq-lagnirac">
</div>

Welcome to the User Manual of Pickler Loan Receipts. This document aims to help
guide an end-user in the daily or regular use of this tool.

If you have any questions, comments, or concerns, plese feel free to reach
out to the [Pickler Memorial Library](https://library.truman.edu)
or the current maintainers of this project.

## Table of Contents

1. [Purpose](#purpose)
1. [Configuration File](#configuration-file)
1. [Printer](#printer)
1. [Patron ID](#patron-id)
1. [Credits and Closing](#credits-and-closing)

## Purpose

This program is intended as an interface to quickly and efficiently print
out check-out loan receipts through a standard thermal receipt printer to
patrons of Pickler Memorial Library at Truman State University. The tool takes
an input Patron ID and sends a print request to a connected printer. This
program was built for internal/in-house usage and not originally intended for
further use beyond Pickler to the wider MOBIUS Consortium.

## Configuration File

The tool requires a configuration file stored in the Javascript Object Notation
format (JSON). The default name of the file is `config.json`, stored in the
same working directory as the tool. This path can be changed with the relevant
field. At minimum, the JSON must have the following keys and values:

- `okapi_url` : The URL to the OKAPI gateway to the FOLIO project, will
    most likely be `https://okapi-mobius.folio.ebsco.com`.
- `tenant` : The tenant ID for the institution. You can find your FOLIO tenant
    by going to: `Apps` &rarr; `Settings` &rarr; `Software versions`. Under
    `Okapi services` find the subheading `Okapi`, then the entry
    `For tenant...`
- `username` : The individual user of the institution. It is recommended that
    you create an account with read-only permissions for using the API. For
    the purposes of this app, the User account must have at least the
    permission `Requests: View`.
- `password` : The password for the associated account.

**Please note:** The generator is case-sensitive. Only include what is in
between the quotation marks part of the labels and not the marks themselves.
Please visit the repository for an editable template config.json file.

## Printer

The tool was tested on and developed for the
**Star Micronics SP700** ESC/POS Dot Matrix Thermal Receipt printer.

The tool has a default printer driver (which can be seen as the default name
in the `Printer Name` field), but the output can be changed by inputting a new
printer name into the field. The list of connected and recognized printers can
be easily found by clicking the `Find printers...` button to the right of the
text field. Copy the name under the `PRINTER NAME` heading and paste the new
name exactly as written into the text field. The tool will strip any leading or
trailing whitespace before attempting to find a local printer. You should not
copy-paste the `PORT NAME` into the input field.

## Patron ID

The tool was developed with the structure of Truman State University's ID card
system in mind; it remains untested on external IDs and is specifically
oriented towards use-cases in Pickler Memorial Library and Truman's campus as a
whole.

Patron ID numbers for Truman are associated with 9-digit Banner ID numbers,
with the values obtained from the card swipes being
`[BANNER ID] + [NUMBER OF CARDS ISSUED]`.
In other words, if Patron Number `123456789` has had an ID card
issued to them `three` times, a possible number extracted from their card would
be the 11-digit number `12345678903`. The program will accept the `9`-digit
Banner ID, the `11`-digit full card ID, and the `14`-digit Community
Borrower ID. The program should accept any barcode in the system, however the
tool remains untested beyond the scope of the ID numbers listed above.

## Credits and Closing

Developed for use and further development on Windows using Python 3.12+.

Tested on and developed for the Star Micronics SP700 ESC/POS Dot Matrix
Thermal Receipt printer. The tool remains untested on other printer makes
and models.

Developed by Technical Services and Systems, Pickler Memorial Library,
Truman State University.

More information can be found by reading the user and developer manuals
associated with the release.

## Timestamp Details

- **USERMANUAL.md originally published:** 2024-11-12, v0.0.0
- **USERMANUAL.md last updated:** 2024-12-02, v1.2.0
- **USERMANUAL.md version:** v1.1
- **Raw ver. info. (for tracking development):** Z2l0aHViQGphcS1sYWduaXJhYw==