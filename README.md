# mbu-dev-shared-components

## Installation

```bash
pip install mbu-dev-shared-components
```

## Intro

This python library contains helper modules for RPA development.
It's based on the need of MBU, but it has been
generalized to be useful for others as well.

## Integrations

### Office365
#### - SharePoint

Helper functions for using SharePoint api. A few examples include:

- Authentication.
- Get list of files from a specified folder.
- Get file from folder.
- Get files from folder.


#### - Excel

This module provides the ExcelReader class to read data from Excel files with .xlsx format.

The ExcelReader class offers methods to read specific cells, rows, and convert the row data to JSON format.
Additionally, it provides functionalities to count the total number of rows and nodes in the JSON data.

- Read cell
- Read cells
- Read rows
- Get row count


### SAP
#### - Invoices

This module provides the InvoiceCreator class to create invoices in SAP.
The InvoiceCreator class offers methods to open a specified business partner, and creat an invoice.

- Open business partner
- Create invoice


### Solteq Tand
#### - Application
#### - Database

This module provides the SolteqTandApp and SolteqTandDatabase class to handle patients data in Solteq Tand.


### Utils
#### - JSON
This module provides a class for manipulating JSON objects by transforming lists
within the JSON into dictionaries with specified keys.

The primary class in this module is JSONManipulator, which contains methods for
converting lists associated with keys in a JSON object into dictionaries.

- Transform all lists
- Insert key value pairs


#### - Fernet Encryptor
This module provides a class for encrypting and decrypting data using the
Fernet symmetric encryption algorithm.

- Encrypts
- Decrypts
