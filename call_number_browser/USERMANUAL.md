# User Manual - Call Number Browser

<div align="center">
    <img src="images/logo-no-background.png"
    width="500px"
    alt="CNB Logo by github@jaq-lagnirac">
</div>

Welcome to the Call Number Browser!

This document aims to help guide an end-user in the daily or regular use of
this tool. Please feel free to reach out if you have any questions.

## Table of Contents

1. [Purpose](#purpose)
1. [Input Call Number](#input-call-number)
1. [Configuration File](#configuration-file)
1. [Output and Formatting](#output-and-formatting)
1. [Credits and Closing](#credits-and-closing)
1. [Timestamp Details](#timestamp-details)

## Purpose

This program is intended as a way to place new call numbers in an existing
database of materials in order to better illustrate where to shelve new items
to the library. The tool is case- and whitespace-sensitive and may result in
different outputs depending on what is typed in due to the lack of an
associated shelvingOrder for the item.

## Input Call Number

Inputted call numbers should be Library of Congress, Dewey Decimal
Classification, or Local Juvenile Fiction numbers, and will be normalized by
the pycallnumber library. Spacing, case, and other extraneous features should
be normalized out by the tool, but in order to ensure the smoothest usage of
this tool, please still pay attention to the inputted call number and ensure
good input. As the old computer science adage goes:"Garbage in, garbage out."

## Configuration File

The tool requires a configuration file stored in the Javascript Object Notation
format (JSON). The default name of the file is "config.json", stored in the
same working directory as the tool. This path can be changed with the relevant
field. At minimum, the JSON must have the following keys and values:
- `okapi_url` : The URL to the OKAPI gateway to the FOLIO project,
    will most likely be `https://okapi-mobius.folio.ebsco.com`.
- `tenant` : The tenant ID for the institution. You can find your FOLIO tenant
    by going to: `Apps` &rarr; `Settings` &rarr; `Software versions`. Under
    `Okapi services` find the subheading `Okapi`, then the entry
    `For tenant...`
- `username` : The individual user of the institution. It is recommended that
    you create an account with read-only permissions for using the API. For
    the purposes of this app, the User account must have at least the
    permission `Requests: View`.
- `password` : The password for the associated account.

**Please note:** The generator is case-sensitive&mdash;the keys must be exact.
Please visit the repository for an editable template config.json file.

## Output and Formatting

After extracting, sorting, and trimming the items from FolioClient, a slice
centered around the inputted call number is outputted to the window of the
tool, showcasing a possible place in the sorted shelvingOrder of the system.

## Credits and Closing

Developed for use and further development on Windows using Python 3.12+.

Developed by [Pickler Memorial Library](https://library.truman.edu/),
[Truman State University](https://www.truman.edu/).

## Timestamp Details

- **USERMANUAL.md originally published:** 2024-04-22, Project v1.1.0
- **USERMANUAL.md last updated:** 2024-04-22, Project v1.1.0
- **USERMANUAL.md version:** v1.1
- **Raw ver. info. (for tracking development):** Z2l0aHViQGphcS1sYWduaXJhYw==