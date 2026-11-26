
from pathlib import Path
import shutil


# ==========================================
# PHASE 1: DIRECTORY VALIDATION
# ==========================================

def get_directory():

    print("===================================")
    print("     AUTOMATED FILE ORGANISER")
    print("===================================")

    folder_path = input(
        "Enter the directory path to organise: "
    ).strip()

    directory = Path(folder_path)

    if directory.exists() and directory.is_dir():

        print("\nDirectory validated successfully!")
        print("Selected directory:", directory)

        return directory

    else:

        print("\nError: Invalid directory path.")

        return None


# ==========================================
# PHASE 2: SCAN FILES
# ==========================================

def scan_files(directory):

    files = []

    print("\nScanning directory...")
    print("-----------------------------------")

    for item in directory.iterdir():

        if item.is_file():

            files.append(item)

            print("File:", item.name)
            print("Extension:", item.suffix)

    print("-----------------------------------")

    print("Total files found:", len(files))

    return files


# ==========================================
# PHASE 3: FILE CATEGORISATION
# ==========================================

FILE_CATEGORIES = {

    "Documents": [
        ".pdf", ".doc", ".docx", ".odt", ".rtf"
    ],

    "Images": [
        ".jpg", ".jpeg", ".png", ".gif",
        ".bmp", ".svg", ".webp"
    ],

    "Spreadsheets": [
        ".xls", ".xlsx", ".csv", ".ods"
    ],

    "Text Files": [
        ".txt", ".md", ".log"
    ],

    "Programs": [
        ".py", ".js", ".html", ".css",
        ".java", ".c", ".cpp", ".php",
        ".exe", ".bat", ".sh"
    ]

}


def categorise_file(file):

    extension = file.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():

        if extension in extensions:

            return category

    return "Others"


def categorise_files(files):

    categorised_files = {}

    for category in FILE_CATEGORIES:

        categorised_files[category] = []

    categorised_files["Others"] = []

    print("\n========== FILE CATEGORISATION ==========")

    for file in files:

        category = categorise_file(file)

        categorised_files[category].append(file)

        print(f"{file.name} --> {category}")

    print("-----------------------------------------")

    for category, category_files in categorised_files.items():

        print(f"{category}: {len(category_files)} file(s)")

    return categorised_files


# ==========================================
# PHASE 4: CREATE DESTINATION FOLDERS
# ==========================================

def create_folders(directory):

    folders = list(FILE_CATEGORIES.keys()) + ["Others"]

    print("\n========== CREATING FOLDERS ==========")

    for folder in folders:

        folder_path = directory / folder

        folder_path.mkdir(exist_ok=True)

        print(f"Folder ready: {folder}/")

    print("-------------------------------------")

    return folders


# ==========================================
# PHASE 5: PREVENT DUPLICATE FILENAMES
# ==========================================

def get_unique_path(destination):

    if not destination.exists():

        return destination

    counter = 1

    while True:

        new_name = (
            f"{destination.stem}_{counter}"
            f"{destination.suffix}"
        )

        new_path = destination.with_name(new_name)

        if not new_path.exists():

            return new_path

        counter += 1


# ==========================================
# PHASE 5: MOVE FILES WITH EXCEPTION HANDLING
# ==========================================

def move_files(categorised_files, directory):

    print("\n========== MOVING FILES ==========")

    # Store successful movement counts
    summary = {
        category: 0
        for category in categorised_files
    }

    # Store failed file details
    failed_files = []

    for category, files in categorised_files.items():

        destination_folder = directory / category

        for file in files:

            try:

                destination = destination_folder / file.name

                # Prevent overwriting existing files
                destination = get_unique_path(destination)

                # Move the file
                shutil.move(str(file), str(destination))

                # Update count only after successful movement
                summary[category] += 1

                print(
                    f"Moved: {file.name} --> "
                    f"{category}/{destination.name}"
                )

            except (OSError, shutil.Error) as error:

                failed_files.append({
                    "filename": file.name,
                    "category": category,
                    "error": str(error)
                })

                print(f"\nFailed to move: {file.name}")
                print("Reason:", error)

    print("---------------------------------")

    return summary, failed_files


# ==========================================
# PHASE 6: DISPLAY FINAL SUMMARY
# ==========================================

def display_summary(total_scanned, summary, failed_files):

    print("\n========== FINAL ORGANISATION SUMMARY ==========")

    print(f"\nTotal files scanned: {total_scanned}")

    print("\nCategory-wise successful movements:")

    print("-----------------------------------------------")

    for category, count in summary.items():

        print(f"{category:<18}: {count} file(s) moved")

    print("-----------------------------------------------")

    total_moved = sum(summary.values())

    total_failed = len(failed_files)

    print(f"Total files successfully moved: {total_moved}")

    print(f"Total files failed: {total_failed}")

    # Display failed file details
    if failed_files:

        print("\n========== FAILED FILE DETAILS ==========")

        for file in failed_files:

            print("\nFile:", file["filename"])

            print("Category:", file["category"])

            print("Reason:", file["error"])

    else:

        print("\nAll files were moved successfully!")

    print("\n================================================")

    print("Organisation process completed!")


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    # Phase 1: Validate directory
    directory = get_directory()

    if directory is None:
        return

    # Phase 2: Scan files
    files = scan_files(directory)

    # Phase 3: Categorise files
    categorised_files = categorise_files(files)

    # Phase 4: Create folders
    create_folders(directory)

    # Phase 5: Move files
    summary, failed_files = move_files(
        categorised_files,
        directory
    )

    # Phase 6: Display final summary
    display_summary(
        len(files),
        summary,
        failed_files
    )


# ==========================================
# PROGRAM EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
