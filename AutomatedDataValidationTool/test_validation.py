import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from config_loader import load_config
from file_reader import read_file
from validator import validate_dataset
from validation_rules import (
    validate_required,
    validate_email,
    validate_phone,
    validate_integer,
    validate_numeric,
    validate_range,
    validate_allowed_values
)


CONFIG = {
    "Name": {
        "required": True
    },
    "Email": {
        "required": True,
        "type": "email"
    },
    "Phone": {
        "required": True,
        "type": "phone",
        "pattern": r"^\+?[0-9]{10,15}$"
    },
    "Age": {
        "required": True,
        "type": "integer",
        "min": 18,
        "max": 60
    },
    "Department": {
        "required": True,
        "allowed_values": ["HR", "IT", "Finance", "Sales"]
    },
    "Salary": {
        "required": True,
        "type": "numeric",
        "min": 10000,
        "max": 100000
    },
    "duplicate_check": {
        "columns": ["Name", "Email"]
    }
}


class ValidationToolTests(unittest.TestCase):

    def test_valid_email(self):
        self.assertTrue(validate_email("test@gmail.com"))

    def test_invalid_email(self):
        self.assertFalse(validate_email("invalid-email"))

    def test_required_field(self):
        self.assertFalse(validate_required(""))

    def test_valid_phone(self):
        self.assertTrue(
            validate_phone("9876543210", r"^\+?[0-9]{10,15}$")
        )

    def test_invalid_phone(self):
        self.assertFalse(
            validate_phone("12345", r"^\+?[0-9]{10,15}$")
        )

    def test_integer(self):
        self.assertTrue(validate_integer(25))
        self.assertFalse(validate_integer(25.5))

    def test_numeric(self):
        self.assertTrue(validate_numeric(35000))
        self.assertFalse(validate_numeric("abc"))

    def test_numeric_range(self):
        self.assertTrue(validate_range(25, 18, 60))
        self.assertFalse(validate_range(17, 18, 60))

    def test_allowed_values(self):
        self.assertTrue(
            validate_allowed_values(
                "IT", ["HR", "IT", "Finance", "Sales"]
            )
        )

        self.assertFalse(
            validate_allowed_values(
                "Marketing", ["HR", "IT", "Finance", "Sales"]
            )
        )

    def test_duplicate_detection(self):

        df = pd.DataFrame({
            "Name": ["Anu", "Anu"],
            "Email": ["anu@gmail.com", "anu@gmail.com"],
            "Phone": ["9876543210", "9876543210"],
            "Age": [25, 25],
            "Department": ["IT", "IT"],
            "Salary": [35000, 35000]
        })

        valid_df, invalid_df, missing_columns, unknown_columns, failures = validate_dataset(
            df, CONFIG
        )

        self.assertEqual(len(invalid_df), 1)
        self.assertEqual(len(valid_df), 1)

        self.assertIn(
            "Duplicate record",
            invalid_df.iloc[0]["Validation_Errors"]
        )

    def test_multiple_errors(self):

        df = pd.DataFrame({
            "Name": [""],
            "Email": ["bad-email"],
            "Phone": ["123"],
            "Age": [15],
            "Department": ["Marketing"],
            "Salary": [200000]
        })

        valid, invalid, missing, unknown, failures = validate_dataset(
            df, CONFIG
        )

        self.assertEqual(len(invalid), 1)

        errors = invalid.iloc[0]["Validation_Errors"]

        self.assertIn("Name", errors)
        self.assertIn("Email", errors)
        self.assertIn("Phone", errors)
        self.assertIn("Age", errors)
        self.assertIn("Department", errors)
        self.assertIn("Salary", errors)

    def test_missing_columns(self):

        df = pd.DataFrame({
            "Name": ["Anu"],
            "Email": ["anu@gmail.com"]
        })

        valid, invalid, missing, unknown, failures = validate_dataset(
            df, CONFIG
        )

        self.assertIn("Phone", missing)
        self.assertIn("Age", missing)
        self.assertIn("Department", missing)
        self.assertIn("Salary", missing)

        self.assertEqual(len(invalid), 1)

    def test_invalid_json(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            path = Path(temp_dir) / "invalid.json"

            path.write_text(
                "{invalid json}",
                encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                load_config(path)

    def test_reusable_configuration(self):

        alternate_config = {
            "Product": {
                "required": True
            },
            "Price": {
                "required": True,
                "type": "numeric",
                "min": 1,
                "max": 5000
            }
        }

        df = pd.DataFrame({
            "Product": ["Laptop", "Phone"],
            "Price": [4000, 2500]
        })

        valid, invalid, missing, unknown, failures = validate_dataset(
            df, alternate_config
        )

        self.assertEqual(len(valid), 2)
        self.assertEqual(len(invalid), 0)

    def test_csv_file_reader(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            path = Path(temp_dir) / "sample.csv"

            pd.DataFrame({
                "Name": ["Anu"]
            }).to_csv(path, index=False)

            df = read_file(path)

            self.assertEqual(len(df), 1)

    def test_excel_file_reader(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            path = Path(temp_dir) / "sample.xlsx"

            pd.DataFrame({
                "Name": ["Anu"]
            }).to_excel(path, index=False)

            df = read_file(path)

            self.assertEqual(len(df), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)