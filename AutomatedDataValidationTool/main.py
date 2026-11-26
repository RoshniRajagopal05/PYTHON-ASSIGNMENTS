from config_loader import load_config
from file_reader import read_file
from validator import validate_dataset
from report_generator import generate_reports
from summary import generate_summary, display_summary


def main():

    print("=" * 55)
    print("          AUTOMATED DATA VALIDATION TOOL")
    print("=" * 55)

    input_file = input(
        "Enter input CSV/Excel file path: "
    ).strip()

    config_file = input(
        "Enter configuration file path "
        "[config/validation_rules.json]: "
    ).strip()

    if not config_file:
        config_file = "config/validation_rules.json"

    try:

        print("\nLoading configuration...")

        config = load_config(config_file)

        print("Configuration loaded successfully.")

        print("\nReading input dataset...")

        df = read_file(input_file)

        print(
            f"Dataset loaded successfully. "
            f"Records: {len(df)}"
        )

        print("\nValidating records...")

        valid_df, invalid_df, missing_columns, unknown_columns, failures = validate_dataset(df, config)

        print("Validation completed.")

        print("\nGenerating reports...")

        valid_path, invalid_path = generate_reports(
            valid_df,
            invalid_df,
            input_file
        )

        print("Reports generated successfully.")

        print(f"Valid report: {valid_path}")

        print(f"Invalid report: {invalid_path}")

        summary = generate_summary(
    total_records=len(df),
    valid_records=len(valid_df),
    invalid_records=len(invalid_df),
    total_failures=failures,
    missing_columns=missing_columns,
    unknown_columns=unknown_columns
)

        display_summary(summary)

    except FileNotFoundError as error:

        print(f"\nFile error: {error}")

    except ValueError as error:

        print(f"\nValidation configuration or data error: {error}")

    except Exception as error:

        print(f"\nUnexpected application error: {error}")


if __name__ == "__main__":
    main()