
# Excel Report Generator

A Python automation tool that reads multiple Excel sales files, validates and cleans the data, calculates sales summaries, and generates a consolidated Excel report.

## Features

- Reads multiple Excel files from a folder.
- Combines sales records into a single dataset.
- Validates and cleans data.
- Calculates total sales per transaction.
- Generates product-wise and category-wise revenue summaries.
- Identifies best-selling products.
- Generates an Excel report with four sheets.
- Supports date-range filtering.
- Handles invalid files and data.

## Technologies Used

- Python
- Pandas
- OpenPyXL

## Project Structure

```text
ExcelReportGenerator/
├── main.py
├── excel_reader.py
├── data_cleaner.py
├── sales_calculator.py
├── report_generator.py
├── date_filter.py
├── sales/
├── test_data/
├── reports/
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Place the Excel sales files inside the `sales/` folder before running the program.

The generated report will be saved in the `reports/` folder as `sales_performance_report.xlsx`.

## Report Sheets

- All Transactions
- Product Summary
- Category Summary
- Overall Summary
