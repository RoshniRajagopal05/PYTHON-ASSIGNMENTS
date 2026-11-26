from pathlib import Path


def generate_reports(
    valid_df,
    invalid_df,
    input_file,
    output_dir="output"
):
    """
    Generate valid and invalid reports.

    CSV input:
        valid_records.csv
        invalid_records.csv

    Excel input:
        valid_records.xlsx
        invalid_records.xlsx
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_extension = Path(input_file).suffix.lower()

    if input_extension == ".csv":

        valid_path = output_dir / "valid_records.csv"
        invalid_path = output_dir / "invalid_records.csv"

        valid_df.to_csv(
            valid_path,
            index=False,
            encoding="utf-8-sig"
        )

        invalid_df.to_csv(
            invalid_path,
            index=False,
            encoding="utf-8-sig"
        )

    elif input_extension == ".xlsx":

        valid_path = output_dir / "valid_records.xlsx"
        invalid_path = output_dir / "invalid_records.xlsx"

        valid_df.to_excel(
            valid_path,
            index=False,
            engine="openpyxl"
        )

        invalid_df.to_excel(
            invalid_path,
            index=False,
            engine="openpyxl"
        )

    else:
        raise ValueError(
            "Unsupported input format for report generation."
        )

    return valid_path, invalid_path