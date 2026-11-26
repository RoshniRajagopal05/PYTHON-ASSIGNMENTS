
from excel_reader import read_excel_files
from data_cleaner import clean_sales_data
from report_generator import generate_excel_report
from date_filter import filter_sales_by_date

from sales_calculator import (
    calculate_transaction_sales,
    calculate_product_summary,
    calculate_category_summary,
    calculate_best_selling_products,
    calculate_overall_summary
)


def main():

    print("\n========== EXCEL REPORT GENERATOR ==========")

    # Step 1: Read Excel files
    folder_path = "sales"

    data = read_excel_files(folder_path)

    if data is None or data.empty:
        print("\nNo valid sales data available.")
        return

    # Step 2: Clean data
    cleaned_data, invalid_records = clean_sales_data(data)

    if cleaned_data.empty:
        print("\nNo valid records available for calculation.")
        return

    # Step 3: Date range filtering
    choice = input(
        "\nDo you want to filter sales by date? (yes/no): "
    ).strip().lower()

    if choice == "yes":

        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")

        try:
            cleaned_data = filter_sales_by_date(
                cleaned_data,
                start_date,
                end_date
            )

            print(f"\nRecords after date filtering: {len(cleaned_data)}")

        except (ValueError, TypeError) as error:
            print(f"\nDate filtering error: {error}")
            return

        if cleaned_data.empty:
            print("\nNo sales records found within the selected date range.")
            return

    elif choice == "no":
        print("\nGenerating report using all valid records.")

    else:
        print("\nInvalid choice. Please enter yes or no.")
        return

    # Step 4: Calculate transaction sales
    sales_data = calculate_transaction_sales(cleaned_data)

    # Step 5: Product summary
    product_summary = calculate_product_summary(sales_data)

    # Step 6: Category summary
    category_summary = calculate_category_summary(sales_data)

    # Step 7: Best-selling products
    best_selling = calculate_best_selling_products(product_summary)

    # Step 8: Overall summary
    overall_summary = calculate_overall_summary(
        sales_data,
        best_selling
    )

    # Step 9: Generate Excel report
    generate_excel_report(
        sales_data,
        product_summary,
        category_summary,
        overall_summary
    )

    # Display results
    print("\n========== TRANSACTION SALES ==========")
    print(sales_data)

    print("\n========== PRODUCT SUMMARY ==========")
    print(product_summary)

    print("\n========== CATEGORY SUMMARY ==========")
    print(category_summary)

    print("\n========== BEST-SELLING PRODUCTS ==========")
    print(best_selling)

    print("\n========== OVERALL SUMMARY ==========")

    for key, value in overall_summary.items():
        print(f"{key}: {value}")

    print("\n========== REPORT GENERATION COMPLETED ==========")


if __name__ == "__main__":
    main()
