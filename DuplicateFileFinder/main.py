import os
import hashlib
import csv
from pathlib import Path


CHUNK_SIZE = 1024 * 1024  # 1 MB


# Convert bytes into a readable format
def format_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)

    for unit in units:
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} TB"


# Validate directory
def validate_directory(folder_path):
    folder = Path(folder_path)

    if not folder.exists():
        print("Error: Directory does not exist.")
        return None

    if not folder.is_dir():
        print("Error: The provided path is not a directory.")
        return None

    return folder


# Recursively collect files
def scan_directory(folder):
    files = []

    try:
        for root, _, filenames in os.walk(folder, onerror=lambda error: print(f"Directory access error: {error}")):
            for filename in filenames:
                file_path = Path(root) / filename

                try:
                    if file_path.is_file():
                        files.append(file_path)
                except OSError as error:
                    print(f"Unable to access file: {file_path}")
                    print(f"Reason: {error}")

    except OSError as error:
        print(f"Scanning error: {error}")

    return files


# Calculate SHA-256 hash using chunk-based reading
def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(CHUNK_SIZE)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    except (OSError, PermissionError) as error:
        print(f"\nUnable to hash: {file_path}")
        print(f"Reason: {error}")
        return None


# Group files by size and hash
def find_duplicates(files):
    size_groups = {}

    # Step 1: Group files by size
    for file_path in files:
        try:
            size = file_path.stat().st_size
            size_groups.setdefault(size, []).append(file_path)

        except OSError as error:
            print(f"Unable to read file size: {file_path}")
            print(f"Reason: {error}")

    hash_groups = {}

    # Step 2: Hash files that share the same size
    for size, file_list in size_groups.items():

        if len(file_list) < 2:
            continue

        for file_path in file_list:
            file_hash = calculate_hash(file_path)

            if file_hash is None:
                continue

            hash_groups.setdefault(file_hash, []).append(file_path)

    # Step 3: Keep only groups containing duplicates
    duplicate_groups = []

    for file_hash, file_list in hash_groups.items():
        if len(file_list) > 1:
            duplicate_groups.append({
                "hash": file_hash,
                "files": file_list
            })

    return duplicate_groups


# Display duplicate report
def display_report(duplicate_groups):

    if not duplicate_groups:
        print("\nNo duplicate files found.")
        return

    total_savings = 0

    print("\n========== DUPLICATE FILE REPORT ==========")

    for group_number, group in enumerate(duplicate_groups, start=1):
        files = group["files"]

        file_size = files[0].stat().st_size
        savings = file_size * (len(files) - 1)
        total_savings += savings

        print(f"\nDuplicate Group {group_number}")
        print("-" * 40)

        for file_path in files:
            print(f"- {file_path}")

        print(f"\nFile Size: {format_size(file_size)}")
        print(f"Total Files: {len(files)}")
        print(f"Duplicate Copies: {len(files) - 1}")
        print(f"Potential Space Savings: {format_size(savings)}")

    print("\n==========================================")
    print(f"Total Potential Savings: {format_size(total_savings)}")
    print("==========================================")


# Export duplicate report to CSV
def export_csv(duplicate_groups, output_file="duplicate_report.csv"):

    if not duplicate_groups:
        print("No duplicates to export.")
        return

    try:
        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:

            writer = csv.writer(csv_file)

            writer.writerow([
                "Group Number",
                "File Path",
                "File Size (Bytes)",
                "File Size (Readable)",
                "SHA256 Hash",
                "Retained File"
            ])

            for group_number, group in enumerate(duplicate_groups, start=1):
                files = group["files"]
                retained_file = files[0]

                for file_path in files:
                    size = file_path.stat().st_size

                    writer.writerow([
                        group_number,
                        str(file_path),
                        size,
                        format_size(size),
                        group["hash"],
                        "Yes" if file_path == retained_file else "No"
                    ])

        print(f"\nCSV report exported successfully: {output_file}")

    except (OSError, PermissionError) as error:
        print(f"\nCSV export failed: {error}")


# Optional manual duplicate removal
def remove_duplicates_manually(duplicate_groups):

    if not duplicate_groups:
        print("\nNo duplicates available for removal.")
        return

    print("\n========== MANUAL DUPLICATE REMOVAL ==========")
    print("The first file in each group is designated as the retained file.")
    print("Only additional copies can be selected for removal.")

    for group_number, group in enumerate(duplicate_groups, start=1):

        files = group["files"]

        print(f"\nGroup {group_number}")
        print("-" * 40)

        for index, file_path in enumerate(files, start=1):

            if index == 1:
                print(f"{index}. [RETAINED] {file_path}")
            else:
                print(f"{index}. [REMOVABLE COPY] {file_path}")

    try:
        group_number = int(input("\nEnter group number to manage (0 to cancel): "))

        if group_number == 0:
            print("Removal cancelled.")
            return

        if group_number < 1 or group_number > len(duplicate_groups):
            print("Invalid group number.")
            return

        group = duplicate_groups[group_number - 1]
        files = group["files"]

        if len(files) < 2:
            print("No removable copies.")
            return

        print("\nSelected duplicate group:")
        print("-" * 40)

        print(f"1. [RETAINED] {files[0]}")

        for index, file_path in enumerate(files[1:], start=2):
            print(f"{index}. {file_path}")

        print("\nThe retained file cannot be selected for deletion.")

        selections = input(
            "\nEnter copy numbers to remove separated by commas (or 0 to cancel): "
        ).strip()

        if selections == "0":
            print("Removal cancelled.")
            return

        selected_numbers = set()

        for value in selections.split(","):
            number = int(value.strip())

            if number < 2 or number > len(files):
                print(f"Invalid copy number: {number}")
                return

            selected_numbers.add(number)

        if not selected_numbers:
            print("No copies selected.")
            return

        selected_files = [files[number - 1] for number in sorted(selected_numbers)]

        print("\nFiles selected for removal:")

        for file_path in selected_files:
            print(f"- {file_path}")

        confirmation = input(
            "\nAre you sure you want to permanently delete these files? (yes/no): "
        ).strip().lower()

        if confirmation != "yes":
            print("Deletion cancelled.")
            return

        for file_path in selected_files:

            try:
                file_path.unlink()
                print(f"Removed: {file_path}")

            except OSError as error:
                print(f"Failed to remove: {file_path}")
                print(f"Reason: {error}")

    except ValueError:
        print("Invalid input. Please enter numbers only.")


# Main application
def main():

    print("=" * 50)
    print("       DUPLICATE FILE FINDER")
    print("=" * 50)

    folder_path = input("\nEnter directory path to scan: ").strip()

    folder = validate_directory(folder_path)

    if folder is None:
        return

    print("\nScanning directory...")

    files = scan_directory(folder)

    print(f"Total files scanned: {len(files)}")

    print("\nAnalyzing file contents...")

    duplicate_groups = find_duplicates(files)

    display_report(duplicate_groups)

    if not duplicate_groups:
        return

    export_choice = input("\nExport report to CSV? (yes/no): ").strip().lower()

    if export_choice == "yes":
        output_path = input(
            "Enter CSV filename (press Enter for duplicate_report.csv): "
        ).strip()

        if not output_path:
            output_path = "duplicate_report.csv"

        export_csv(duplicate_groups, output_path)

    removal_choice = input(
        "\nDo you want to manually remove selected duplicate copies? (yes/no): "
    ).strip().lower()

    if removal_choice == "yes":
        remove_duplicates_manually(duplicate_groups)

    print("\nDuplicate File Finder completed.")
    print("==========================================")


if __name__ == "__main__":
    main()