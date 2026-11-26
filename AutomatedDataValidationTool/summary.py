def generate_summary(
    total_records,
    valid_records,
    invalid_records,
    total_failures,
    missing_columns=None,
    unknown_columns=None
):
    success_percentage = (
        (valid_records / total_records) * 100
        if total_records > 0 else 0
    )

    summary = {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "total_validation_failures": total_failures,
        "success_percentage": round(success_percentage, 2),
        "missing_columns": missing_columns or [],
        "unknown_columns": unknown_columns or []
    }

    return summary


def display_summary(summary):
    print("\n" + "=" * 50)
    print("          VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total records processed : {summary['total_records']}")
    print(f"Valid records          : {summary['valid_records']}")
    print(f"Invalid records        : {summary['invalid_records']}")
    print(f"Validation failures    : {summary['total_validation_failures']}")
    print(f"Success percentage     : {summary['success_percentage']}%")

    if summary["missing_columns"]:
        print("Missing columns        : " + ", ".join(summary["missing_columns"]))
    else:
        print("Missing columns        : None")

    if summary["unknown_columns"]:
        print("Unknown columns        : " + ", ".join(summary["unknown_columns"]))
    else:
        print("Unknown columns        : None")

    print("=" * 50)