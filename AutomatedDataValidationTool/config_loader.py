import json
from pathlib import Path


SUPPORTED_TYPES = {"email", "phone", "integer", "numeric"}


def load_config(config_path):
    """
    Load validation configuration from a JSON file.
    """

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON configuration: {error}"
        ) from error

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a JSON object.")

    validate_config_structure(config)

    return config


def validate_config_structure(config):
    """
    Validate the structure and supported rules
    of the configuration.
    """

    if not config:
        raise ValueError("Configuration cannot be empty.")

    for column, rules in config.items():

        if column == "duplicate_check":
            validate_duplicate_config(rules)
            continue

        if not isinstance(rules, dict):
            raise ValueError(
                f"Rules for column '{column}' must be an object."
            )

        allowed_keys = {
            "required",
            "type",
            "min",
            "max",
            "allowed_values",
            "pattern"
        }

        unknown_keys = set(rules.keys()) - allowed_keys

        if unknown_keys:
            raise ValueError(
                f"Unknown rules for '{column}': {unknown_keys}"
            )

        if "required" in rules and not isinstance(
            rules["required"], bool
        ):
            raise ValueError(
                f"'required' for '{column}' must be boolean."
            )

        if "type" in rules:

            data_type = rules["type"]

            if data_type not in SUPPORTED_TYPES:
                raise ValueError(
                    f"Unsupported type '{data_type}' "
                    f"for column '{column}'."
                )

        if "min" in rules and "max" in rules:

            if rules["min"] > rules["max"]:
                raise ValueError(
                    f"Minimum value exceeds maximum "
                    f"for column '{column}'."
                )

        if "allowed_values" in rules:

            if not isinstance(rules["allowed_values"], list):
                raise ValueError(
                    f"'allowed_values' for '{column}' "
                    f"must be a list."
                )

        if "pattern" in rules:

            if not isinstance(rules["pattern"], str):
                raise ValueError(
                    f"'pattern' for '{column}' must be a string."
                )


def validate_duplicate_config(rules):
    """
    Validate duplicate-check configuration.
    """

    if not isinstance(rules, dict):
        raise ValueError(
            "'duplicate_check' must be an object."
        )

    if "columns" not in rules:
        raise ValueError(
            "'duplicate_check' must contain 'columns'."
        )

    columns = rules["columns"]

    if not isinstance(columns, list) or not columns:
        raise ValueError(
            "'duplicate_check.columns' must be a non-empty list."
        )

    if not all(isinstance(column, str) for column in columns):
        raise ValueError(
            "Duplicate-check columns must contain column names."
        )