# Automated Data Validation Tool

## Overview

The Automated Data Validation Tool is a standalone Python command-line application designed to validate CSV and Excel datasets using configurable JSON validation rules.

It identifies invalid records, detects duplicate data, checks missing and unexpected columns, and generates separate reports for valid and invalid records.

## Features

- Supports CSV and Excel (.xlsx) input files.
- JSON-based, reusable validation configurations.
- Required field validation.
- Email format validation.
- Phone number validation using configurable regular expressions.
- Integer validation.
- Numeric validation.
- Minimum and maximum range validation.
- Allowed-value validation.
- Duplicate record detection.
- Missing column detection.
- Unknown column detection.
- Preserves original dataset values.
- Generates separate valid and invalid reports.
- Includes validation error descriptions for invalid records.
- Displays validation summary statistics.
- Handles missing files, empty datasets, unsupported file formats and invalid configurations.
- Includes unit tests.

## Project Structure

```text
AutomatedDataValidationTool/
│
├── main.py
├── config_loader.py
├── file_reader.py
├── validator.py
├── validation_rules.py
├── report_generator.py
├── summary.py
├── test_validation.py
├── requirements.txt
│
├── config/
│   └── validation_rules.json
│
├── test_data/
│   ├── sample_data.csv
│   └── sample_data.xlsx
│
├── output/
│
└── README.md
```

## Technologies Used

- Python
- Pandas
- OpenPyXL
- JSON
- unittest

## Installation

### 1. Clone or download the project

Navigate to the project directory.

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Validation rules are defined in:

```text
config/validation_rules.json
```

Example:

```json
{
    "Name": {
        "required": true
    },
    "Email": {
        "required": true,
        "type": "email"
    },
    "Phone": {
        "required": true,
        "type": "phone",
        "pattern": "^\\+?[0-9]{10,15}$"
    },
    "Age": {
        "required": true,
        "type": "integer",
        "min": 18,
        "max": 60
    },
    "Department": {
        "required": true,
        "allowed_values": ["HR", "IT", "Finance", "Sales"]
    },
    "Salary": {
        "required": true,
        "type": "numeric",
        "min": 10000,
        "max": 100000
    },
    "duplicate_check": {
        "columns": ["Name", "Email"]
    }
}
```

### Supported validation rules

| Rule | Description |
|---|---|
| required | Checks whether a field is missing or empty. |
| email | Validates email format. |
| phone | Validates phone numbers using a regex pattern. |
| integer | Checks whether a value is an integer. |
| numeric | Checks whether a value is numeric. |
| min | Defines the minimum permitted value. |
| max | Defines the maximum permitted value. |
| allowed_values | Restricts values to a specified list. |
| duplicate_check | Identifies duplicate records based on configured columns. |

## Usage

Run the application:

```bash
python main.py
```

The application prompts for:

1. Input CSV or Excel file path.
2. Configuration file path (optional).

If the configuration path is left empty, the default configuration is used:

```text
config/validation_rules.json
```

## Output Reports

Reports are generated in the `output/` directory.

### CSV input

- `valid_records.csv`
- `invalid_records.csv`

### Excel input

- `valid_records.xlsx`
- `invalid_records.xlsx`

Invalid records contain a `Validation_Errors` column describing the validation issues.

## Validation Summary

The application displays:

- Total records processed.
- Valid records.
- Invalid records.
- Total validation failures.
- Success percentage.
- Missing columns.
- Unknown columns.

## Testing

Run the unit test suite:

```bash
python -m unittest test_validation.py
```

The test suite covers validation functions, duplicate detection, missing columns, reusable configurations, file reading and other validation scenarios.

## Error Handling

The application handles:

- Missing input files.
- Missing configuration files.
- Invalid JSON configuration files.
- Unsupported file formats.
- Empty CSV files.
- Datasets containing no records.
- Validation configuration errors.

## Limitations

- Supports CSV and `.xlsx` files.
- Validation rules are configured using JSON.
- The application operates locally and does not require a database.

## License

This project was developed as a Python programming assignment.
