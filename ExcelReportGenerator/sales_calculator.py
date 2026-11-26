import pandas as pd


def calculate_transaction_sales(data):
    """
    Calculate total sales for each transaction.
    Total Sales = Quantity * Unit Price
    """
    data = data.copy()

    data["Total Sales"] = data["Quantity"] * data["Unit Price"]

    return data


def calculate_product_summary(data):
    """
    Calculate total quantity sold and revenue for each product.
    """
    product_summary = data.groupby("Product").agg(
        Total_Quantity_Sold=("Quantity", "sum"),
        Total_Revenue=("Total Sales", "sum")
    ).reset_index()

    product_summary = product_summary.sort_values(
        by="Total_Quantity_Sold",
        ascending=False
    )

    return product_summary


def calculate_category_summary(data):
    """
    Calculate total revenue for each category.
    """
    category_summary = data.groupby("Category").agg(
        Total_Revenue=("Total Sales", "sum")
    ).reset_index()

    return category_summary


def calculate_best_selling_products(product_summary):
    """
    Identify all products with the highest quantity sold.
    Handles ties.
    """
    if product_summary.empty:
        return []

    highest_quantity = product_summary["Total_Quantity_Sold"].max()

    best_selling = product_summary.loc[
        product_summary["Total_Quantity_Sold"] == highest_quantity,
        "Product"
    ].tolist()

    return best_selling


def calculate_overall_summary(data, best_selling):
    """
    Calculate overall sales statistics.
    """
    overall_summary = {
        "Overall Revenue": data["Total Sales"].sum(),
        "Total Transactions": len(data),
        "Total Quantity Sold": data["Quantity"].sum(),
        "Best-Selling Product(s)": ", ".join(best_selling)
    }

    return overall_summary