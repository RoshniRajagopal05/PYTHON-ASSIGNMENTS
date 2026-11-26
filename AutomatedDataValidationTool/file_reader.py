import pandas as pd
from pathlib import Path


def read_file(file_path):
    """
    Read CSV or Excel file and return a DataFrame.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    file_extension = file_path.suffix.lower()

    if file_extension == ".csv":

        try:
            df = pd.read_csv(file_path)

        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty.")

    elif file_extension == ".xlsx":

        try:
            df = pd.read_excel(file_path, engine="openpyxl")

        except Exception as error:
            raise ValueError(
                f"Unable to read Excel file: {error}"
            ) from error

    else:
        raise ValueError(
            "Unsupported file format. "
            "Please provide a CSV or Excel file."
        )

    if df.empty:
        raise ValueError(
            "The dataset contains no records."
        )

    if len(df.columns) == 0:
        raise ValueError(
            "The dataset contains no columns."
        )

    return df