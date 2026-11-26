
import re
from pathlib import Path

import pandas as pd


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


# ==========================================
# PHASE 1: GET AND VALIDATE CSV FILE
# ==========================================

def get_csv_file_path():
    file_path = input("\nEnter CSV file path: ").strip()
    return Path(file_path)


def validate_csv_file(file_path):
    if not file_path.exists():
        print("\nError: File does not exist!")
        return False

    if not file_path.is_file():
        print("\nError: The provided path is not a file!")
        return False

    if file_path.suffix.lower() != ".csv":
        print("\nError: Please provide a CSV file!")
        return False

    return True


# ==========================================
# PHASE 2: READ CSV FILE
# ==========================================

def read_csv_file(file_path):
    try:
        dataframe = pd.read_csv(
            file_path,
            dtype={"Phone": "string"}
        )

        if dataframe.empty:
            print("\nWarning: The CSV file contains no records.")

        print("\nCSV file read successfully!")
        return dataframe

    except pd.errors.EmptyDataError:
        print("\nError: The CSV file is empty!")

    except pd.errors.ParserError:
        print("\nError: Unable to parse the CSV file!")

    except UnicodeDecodeError:
        print("\nError: Unable to decode the CSV file!")

    except OSError as error:
        print(f"\nFile reading error: {error}")

    return None


def display_dataset(dataframe, title):
    print(f"\n========== {title} ==========")
    print(dataframe)

    print("\n========== DATASET SUMMARY ==========")
    print(f"Total Records : {len(dataframe)}")
    print(f"Total Columns : {len(dataframe.columns)}")


# ==========================================
# PHASE 3: CLEAN TEXT FIELDS
# ==========================================

def clean_text_fields(dataframe):
    text_columns = dataframe.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        dataframe[column] = (
            dataframe[column]
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    print("\nText fields cleaned successfully!")
    return dataframe


def standardize_city_names(dataframe):
    if "City" in dataframe.columns:
        dataframe["City"] = dataframe["City"].str.title()
        print("\nCity names standardised successfully!")
    else:
        print("\nCity column not found. Skipping city standardisation.")

    return dataframe


# ==========================================
# PHASE 4: DUPLICATE DETECTION AND REMOVAL
# ==========================================

def identify_duplicates(dataframe):
    duplicate_records = dataframe[
        dataframe.duplicated()
    ]

    print("\n========== DUPLICATE RECORDS ==========")
    print(duplicate_records)

    duplicate_count = len(duplicate_records)

    print(f"\nTotal duplicate records found: {duplicate_count}")

    return duplicate_count


def remove_duplicates(dataframe):
    original_count = len(dataframe)

    cleaned_dataframe = dataframe.drop_duplicates(
        keep="first"
    )

    cleaned_dataframe = cleaned_dataframe.reset_index(drop=True)

    duplicates_removed = original_count - len(cleaned_dataframe)

    print("\n========== DUPLICATE SUMMARY ==========")
    print(f"Total Records Before Cleaning : {original_count}")
    print(f"Duplicates Removed            : {duplicates_removed}")
    print(f"Records After Cleaning        : {len(cleaned_dataframe)}")

    return cleaned_dataframe, duplicates_removed


# ==========================================
# PHASE 5: DATA VALIDATION
# ==========================================

def select_mandatory_columns(dataframe):
    available_columns = list(dataframe.columns)

    print("\n========== AVAILABLE COLUMNS ==========")

    for index, column in enumerate(available_columns, start=1):
        print(f"{index}. {column}")

    print("\nChoose which columns should be mandatory.")
    print("Enter column numbers separated by commas.")
    print("Example: 1,2")

    while True:
        user_input = input(
            "\nEnter mandatory column numbers: "
        ).strip()

        selected_numbers = [
            item.strip()
            for item in user_input.split(",")
            if item.strip()
        ]

        if not selected_numbers:
            print("Error: Please select at least one column.")
            continue

        try:
            column_numbers = [
                int(number)
                for number in selected_numbers
            ]

        except ValueError:
            print("Error: Enter valid numbers only.")
            continue

        if any(
            number < 1 or number > len(available_columns)
            for number in column_numbers
        ):
            print("Error: One or more column numbers are invalid.")
            continue

        if len(column_numbers) != len(set(column_numbers)):
            print("Error: Duplicate column selections are not allowed.")
            continue

        mandatory_columns = [
            available_columns[number - 1]
            for number in column_numbers
        ]

        print("\nSelected mandatory columns:")
        for column in mandatory_columns:
            print(f"- {column}")

        return mandatory_columns


def validate_mandatory_fields(row, mandatory_columns):
    errors = []

    for column in mandatory_columns:
        value = row[column]

        if pd.isna(value) or str(value).strip() == "":
            errors.append(
                f"Missing mandatory field: {column}"
            )

    return errors


def validate_email(email):
    email_pattern = (
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    return bool(
        re.fullmatch(email_pattern, str(email).strip())
    )


def validate_records(dataframe, mandatory_columns):
    valid_records = []
    invalid_records = []

    for _, row in dataframe.iterrows():
        errors = validate_mandatory_fields(
            row,
            mandatory_columns
        )

        # Validate a non-empty Email value whenever
        # an Email column is available.
        if "Email" in dataframe.columns:
            email = row["Email"]

            if (
                pd.notna(email)
                and str(email).strip() != ""
                and not validate_email(email)
            ):
                errors.append("Invalid email format")

        record = row.to_dict()

        if errors:
            record["Error Reason"] = "; ".join(errors)
            invalid_records.append(record)
        else:
            valid_records.append(record)

    valid_dataframe = pd.DataFrame(
        valid_records,
        columns=dataframe.columns
    )

    invalid_dataframe = pd.DataFrame(
        invalid_records,
        columns=list(dataframe.columns) + ["Error Reason"]
    )

    print("\n========== VALIDATION SUMMARY ==========")
    print(f"Total Records   : {len(dataframe)}")
    print(f"Valid Records   : {len(valid_dataframe)}")
    print(f"Invalid Records : {len(invalid_dataframe)}")

    return valid_dataframe, invalid_dataframe


# ==========================================
# PHASE 6: GENERATE CSV REPORTS
# ==========================================

def create_output_directory():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nOutput directory ready!")


def generate_csv_reports(valid_dataframe, invalid_dataframe):
    cleaned_file = OUTPUT_DIR / "cleaned_customers.csv"
    invalid_file = OUTPUT_DIR / "invalid_records.csv"

    try:
        valid_dataframe.to_csv(
            cleaned_file,
            index=False
        )

        invalid_dataframe.to_csv(
            invalid_file,
            index=False
        )

        print("\n========== REPORT GENERATION ==========")

        print("\nCleaned CSV generated successfully!")
        print(f"Location: {cleaned_file}")

        print("\nInvalid records report generated successfully!")
        print(f"Location: {invalid_file}")

        return True

    except OSError as error:
        print(f"\nError generating CSV reports: {error}")
        return False


def display_final_summary(
    total_records,
    duplicates_removed,
    valid_records,
    invalid_records
):
    print("\n====================================")
    print("       PROCESSING SUMMARY")
    print("====================================")

    print(f"Total Records Processed : {total_records}")
    print(f"Duplicates Removed      : {duplicates_removed}")
    print(f"Valid Records           : {valid_records}")
    print(f"Invalid Records         : {invalid_records}")

    print("\n====================================")


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():
    print("\n====================================")
    print("       CSV DATA CLEANER")
    print("====================================")

    # Get CSV file path
    file_path = get_csv_file_path()

    # Validate file
    if not validate_csv_file(file_path):
        return

    # Read CSV
    dataframe = read_csv_file(file_path)

    if dataframe is None:
        return

    # Store original record count
    total_records = len(dataframe)

    display_dataset(dataframe, "ORIGINAL DATASET")

    # Clean text fields
    dataframe = clean_text_fields(dataframe)

    # Standardise city names
    dataframe = standardize_city_names(dataframe)

    # Identify duplicates
    identify_duplicates(dataframe)

    # Remove duplicates
    dataframe, duplicates_removed = remove_duplicates(
        dataframe
    )

    # Select mandatory columns dynamically
    mandatory_columns = select_mandatory_columns(
        dataframe
    )

    # Validate records
    valid_dataframe, invalid_dataframe = validate_records(
        dataframe,
        mandatory_columns
    )

    # Create output directory
    create_output_directory()

    # Generate reports
    reports_generated = generate_csv_reports(
        valid_dataframe,
        invalid_dataframe
    )

    if reports_generated:
        display_final_summary(
            total_records,
            duplicates_removed,
            len(valid_dataframe),
            len(invalid_dataframe)
        )


if __name__ == "__main__":
    main()
