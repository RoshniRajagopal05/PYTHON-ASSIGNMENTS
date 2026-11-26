import pandas as pd


def filter_sales_by_date(data, start_date, end_date):

    data = data.copy()

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    filtered_data = data[
        (data["Date"] >= start_date) &
        (data["Date"] <= end_date)
    ]

    return filtered_data