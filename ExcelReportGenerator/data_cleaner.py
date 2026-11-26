
import pandas as pd


def clean_sales_data(data):

    df = data.copy()

    # Store validation errors
    invalid_records = []

    # Convert dates into datetime format
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        dayfirst=True
    )

    # Validate product and category
    for column in ["Product", "Category"]:

        df[column] = df[column].astype("string").str.strip()

    # Convert numeric columns
    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    df["Unit Price"] = pd.to_numeric(
        df["Unit Price"],
        errors="coerce"
    )

    # Validate each transaction
    for index, row in df.iterrows():

        errors = []

        # Date validation
        if pd.isna(row["Date"]):
            errors.append("Invalid or missing Date")

        # Product validation
        if pd.isna(row["Product"]) or row["Product"] == "":
            errors.append("Missing Product")

        # Category validation
        if pd.isna(row["Category"]) or row["Category"] == "":
            errors.append("Missing Category")

        # Quantity validation
        quantity = row["Quantity"]

        if pd.isna(quantity):
            errors.append("Missing or invalid Quantity")

        elif quantity <= 0 or quantity % 1 != 0:
            errors.append("Quantity must be a positive whole number")

        # Unit Price validation
        price = row["Unit Price"]

        if pd.isna(price):
            errors.append("Missing or invalid Unit Price")

        elif price < 0:
            errors.append("Unit Price cannot be negative")

        # Store invalid records
        if errors:

            invalid_records.append({
                "File": row["Source File"],
                "Excel Row": row["Source Row"],
                "Errors": ", ".join(errors)
            })

    # Identify valid records
    invalid_indices = [
        index
        for index, row in df.iterrows()
        if any(
            record["File"] == row["Source File"]
            and record["Excel Row"] == row["Source Row"]
            for record in invalid_records
        )
    ]

    cleaned_data = df.drop(
        index=invalid_indices
    ).copy()

    # Convert valid quantities to integers
    cleaned_data["Quantity"] = (
        cleaned_data["Quantity"].astype(int)
    )

    cleaned_data = cleaned_data.reset_index(drop=True)

    return cleaned_data, invalid_records
