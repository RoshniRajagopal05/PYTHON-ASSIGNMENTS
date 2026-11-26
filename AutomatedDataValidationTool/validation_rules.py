import re
import pandas as pd


def is_missing(value):
    """
    Check whether a value is missing or empty.
    """

    if pd.isna(value):
        return True

    if isinstance(value, str) and value.strip() == "":
        return True

    return False


def validate_required(value):
    """
    Validate mandatory fields.
    """

    return not is_missing(value)


def validate_email(value):
    """
    Validate basic email format.
    """

    if is_missing(value):
        return False

    pattern = (
        r"^[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    return bool(re.fullmatch(pattern, str(value).strip()))


def validate_phone(value, pattern):
    """
    Validate phone number against configured regex.
    """

    if is_missing(value):
        return False

    return bool(
        re.fullmatch(pattern, str(value).strip())
    )


def validate_integer(value):
    """
    Validate whether a value is an integer.
    """

    if is_missing(value):
        return False

    try:
        numeric_value = float(value)

        return (
            numeric_value.is_integer()
        )

    except (ValueError, TypeError):
        return False


def validate_numeric(value):
    """
    Validate whether a value is numeric.
    """

    if is_missing(value):
        return False

    try:
        float(value)
        return True

    except (ValueError, TypeError):
        return False


def validate_range(value, minimum=None, maximum=None):
    """
    Validate numeric minimum and maximum.
    """

    if not validate_numeric(value):
        return False

    numeric_value = float(value)

    if minimum is not None and numeric_value < minimum:
        return False

    if maximum is not None and numeric_value > maximum:
        return False

    return True


def validate_allowed_values(value, allowed_values):
    """
    Validate values against an allowed list.
    """

    if is_missing(value):
        return False

    return value in allowed_values