import pandas as pd
from pathlib import Path


def generate_excel_report(
    sales_data,
    product_summary,
    category_summary,
    overall_summary
):

    reports_folder = Path("reports")
    reports_folder.mkdir(exist_ok=True)

    report_path = reports_folder / "sales_performance_report.xlsx"

    overall_summary_df = pd.DataFrame(
        list(overall_summary.items()),
        columns=["Metric", "Value"]
    )

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:

        sales_data.to_excel(
            writer,
            sheet_name="All Transactions",
            index=False
        )

        product_summary.to_excel(
            writer,
            sheet_name="Product Summary",
            index=False
        )

        category_summary.to_excel(
            writer,
            sheet_name="Category Summary",
            index=False
        )

        overall_summary_df.to_excel(
            writer,
            sheet_name="Overall Summary",
            index=False
        )

        # Automatically adjust column widths
        for worksheet in writer.sheets.values():

            for column_cells in worksheet.columns:

                column_letter = column_cells[0].column_letter

                max_length = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column_cells
                )

                worksheet.column_dimensions[column_letter].width = max_length + 3

    print("\nExcel report generated successfully!")
    print(f"Report location: {report_path.resolve()}")

    return report_path