
import pandas as pd
from pathlib import Path


REQUIRED_COLUMNS = [
    "Date",
    "Product",
    "Category",
    "Quantity",
    "Unit Price"
]


def read_excel_files(folder_path):

    folder = Path(folder_path)

    # Validate folder
    if not folder.exists():
        print("Error: Folder does not exist!")
        return None

    if not folder.is_dir():
        print("Error: Provided path is not a folder!")
        return None

    # Find Excel files and ignore temporary files
    excel_files = sorted(
        file for file in folder.glob("*.xlsx")
        if not file.name.startswith("~$")
    )

    if not excel_files:
        print("No Excel files found!")
        return None

    dataframes = []

    for file in excel_files:

        try:
            print(f"\nReading: {file.name}")

            df = pd.read_excel(
                file,
                engine="openpyxl"
            )

            # Clean column names
            df.columns = df.columns.astype(str).str.strip()

            # Check required columns
            missing_columns = [
                column for column in REQUIRED_COLUMNS
                if column not in df.columns
            ]

            if missing_columns:

                print(
                    f"[FILE ERROR] {file.name}: "
                    f"Missing columns: {', '.join(missing_columns)}"
                )

                continue

            df = df[REQUIRED_COLUMNS].copy()

            # Add source information
            df["Source File"] = file.name

            df["Source Row"] = range(
                2, len(df) + 2
            )

            dataframes.append(df)

        except Exception as error:

            print(
                f"[FILE ERROR] {file.name}: {error}"
            )

    if not dataframes:
        print("No valid Excel files could be processed!")
        return None

    # Combine DataFrames
    combined_data = pd.concat(
        dataframes,
        ignore_index=True
    )

    return combined_data
