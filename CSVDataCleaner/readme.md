# CSV Data Cleaner

A Python application that cleans CSV files by removing duplicate records, standardising text values, and validating data. It generates separate reports for valid and invalid records.

## Features

- Read CSV files using Pandas.
- Remove duplicate records.
- Remove unnecessary spaces from text fields.
- Standardise city names.
- Validate mandatory fields dynamically selected by the user.
- Validate email addresses.
- Generate separate CSV reports for valid and invalid records.

## Technologies Used

- Python 3.12
- Pandas

## Project Structure

```text
CSVDataCleaner/
├── csv_data_cleaner.py
├── requirements.txt
├── test_data/
├── output/
└── README.md
```

## How to Run

1. Clone or download the project.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python csv_data_cleaner.py
   ```

4. Enter the CSV file path when prompted.
5. Select the mandatory columns for validation.

## Output

The application generates the following files inside the `output/` directory:

- `cleaned_customers.csv` – Contains cleaned and valid records.
- `invalid_records.csv` – Contains invalid records along with error reasons.

The original CSV file remains unchanged.