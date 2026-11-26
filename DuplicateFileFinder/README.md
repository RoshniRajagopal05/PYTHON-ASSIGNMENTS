# Duplicate File Finder

A Python utility that recursively scans a directory, identifies duplicate files based on their content using SHA256 hashing, and reports potential storage savings. It also supports CSV report generation and optional manual duplicate removal.

## Features

- Recursively scans directories.
- Identifies duplicate files using SHA256 hashing.
- Groups duplicate files based on content.
- Calculates potential storage savings.
- Exports duplicate details to CSV.
- Supports optional manual duplicate removal with confirmation.
- Handles file access errors.

## Technologies Used

- Python
- `hashlib`
- `os`
- `pathlib`
- `csv`

## How to Run

1. Clone or download the project.
2. Navigate to the project directory.
3. Run:

```bash
python main.py
```

4. Enter the directory path you want to scan.

## Output

- Displays duplicate file groups and potential storage savings.
- Optionally generates `duplicate_report.csv`.

**Note:** Files are not deleted automatically. Removal requires manual selection and confirmation.