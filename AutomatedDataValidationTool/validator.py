import pandas as pd

from validation_rules import (
    is_missing,
    validate_required,
    validate_email,
    validate_phone,
    validate_integer,
    validate_numeric,
    validate_range,
    validate_allowed_values
)


def validate_dataset(df, config):
    """
    Validate a DataFrame using dynamic configuration.

    Returns:
        valid_df
        invalid_df
        missing_columns
        unknown_columns
        total_failures
    """

    df = df.copy()

    # Identify all configured columns, including duplicate-check columns.
    configured_columns = [
        column for column in config
        if column != "duplicate_check"
    ]

    duplicate_config = config.get("duplicate_check")

    if duplicate_config:
        for column in duplicate_config["columns"]:
            if column not in configured_columns:
                configured_columns.append(column)

    # Identify missing and unexpected columns.
    missing_columns = [
        column for column in configured_columns
        if column not in df.columns
    ]

    unknown_columns = [
        column for column in df.columns
        if column not in configured_columns
    ]

    # Add missing configured columns so they can be validated.
    for column in missing_columns:
        df[column] = pd.NA

    errors_per_record = [[] for _ in range(len(df))]

    # Validate individual column rules.
    for column, rules in config.items():

        if column == "duplicate_check":
            continue

        for index, value in enumerate(df[column]):

            record_errors = errors_per_record[index]

            if rules.get("required", False):

                if not validate_required(value):
                    record_errors.append(
                        f"{column}: Required field is missing."
                    )

            if is_missing(value):
                continue

            data_type = rules.get("type")

            if data_type == "email":

                if not validate_email(value):
                    record_errors.append(
                        f"{column}: Invalid email format."
                    )

            elif data_type == "phone":

                pattern = rules.get("pattern")

                if not pattern:
                    record_errors.append(
                        f"{column}: Phone validation pattern "
                        "is not configured."
                    )

                elif not validate_phone(value, pattern):
                    record_errors.append(
                        f"{column}: Invalid phone number."
                    )

            elif data_type == "integer":

                if not validate_integer(value):
                    record_errors.append(
                        f"{column}: Value must be an integer."
                    )

                else:
                    if not validate_range(
                        value,
                        rules.get("min"),
                        rules.get("max")
                    ):
                        record_errors.append(
                            f"{column}: Value must be between "
                            f"{rules.get('min')} and "
                            f"{rules.get('max')}."
                        )

            elif data_type == "numeric":

                if not validate_numeric(value):
                    record_errors.append(
                        f"{column}: Value must be numeric."
                    )

                elif not validate_range(
                    value,
                    rules.get("min"),
                    rules.get("max")
                ):
                    record_errors.append(
                        f"{column}: Value must be between "
                        f"{rules.get('min')} and "
                        f"{rules.get('max')}."
                    )

            if "allowed_values" in rules:

                if not validate_allowed_values(
                    value,
                    rules["allowed_values"]
                ):
                    record_errors.append(
                        f"{column}: Value must be one of "
                        f"{rules['allowed_values']}."
                    )

    # Duplicate validation.
    duplicate_config = config.get("duplicate_check")

    if duplicate_config:

        duplicate_columns = duplicate_config["columns"]

        duplicate_mask = df.duplicated(
            subset=duplicate_columns,
            keep="first"
        )

        for index, is_duplicate in enumerate(duplicate_mask):

            if is_duplicate:
                errors_per_record[index].append(
                    "Duplicate record based on columns: "
                    f"{duplicate_columns}."
                )

    # Store validation errors alongside original records.
    result_df = df.copy()

    result_df["Validation_Errors"] = [
        "; ".join(errors)
        for errors in errors_per_record
    ]

    valid_mask = result_df["Validation_Errors"] == ""

    valid_df = result_df[valid_mask].copy()
    invalid_df = result_df[~valid_mask].copy()

    # Count individual validation failures.
    total_failures = sum(
        len(errors)
        for errors in errors_per_record
    )

    return (
        valid_df,
        invalid_df,
        missing_columns,
        unknown_columns,
        total_failures
    )