from pathlib import Path
from datetime import datetime
import re
import uuid


# --------------------------------------------------
# 1. VALIDATE FOLDER PATH
# --------------------------------------------------

def get_folder_path():
    while True:
        folder_input = input("\nEnter folder path: ").strip().strip('"')
        folder = Path(folder_input)

        if folder.exists() and folder.is_dir():
            return folder

        print("Error: Invalid folder path. Please try again.")


# --------------------------------------------------
# 2. VALIDATE PREFIX
# --------------------------------------------------

def get_prefix():
    while True:
        prefix = input("Enter filename prefix: ").strip()

        # Allow letters, numbers, spaces, underscores and hyphens
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]*", prefix):
            return prefix

        print(
            "Invalid prefix. Use letters, numbers, "
            "spaces, underscores or hyphens."
        )


# --------------------------------------------------
# 3. VALIDATE STARTING NUMBER
# --------------------------------------------------

def get_starting_number():
    while True:
        try:
            number = int(input("Enter starting number: "))

            if number >= 0:
                return number

            print("Starting number cannot be negative.")

        except ValueError:
            print("Please enter a valid integer.")


# --------------------------------------------------
# 4. SELECT FILE EXTENSIONS
# --------------------------------------------------

def get_file_types():
    print("\nEnter file extensions separated by commas.")
    print("Example: .jpg, .png, .pdf")
    print("Enter 'all' to select every file.")

    while True:
        user_input = input("File types: ").strip().lower()

        if user_input == "all":
            return None

        extensions = {
            extension.strip()
            for extension in user_input.split(",")
            if extension.strip()
        }

        if not extensions:
            print("Please enter at least one extension or 'all'.")
            continue

        # Normalize extensions
        extensions = {
            ext if ext.startswith(".") else "." + ext
            for ext in extensions
        }

        # Validate extension format
        if all(re.fullmatch(r"\.[a-z0-9]+", ext) for ext in extensions):
            return extensions

        print("Invalid extension. Example: .jpg, .png")


# --------------------------------------------------
# 5. SCAN DIRECTORY
# --------------------------------------------------

def scan_files(folder):
    try:
        files = [
            file for file in folder.iterdir()
            if file.is_file()
        ]

        # Consistent, case-insensitive sorting
        return sorted(files, key=lambda file: (file.name.lower(), file.name))

    except OSError as error:
        print(f"Unable to scan directory: {error}")
        return []


# --------------------------------------------------
# 6. FILTER FILES
# --------------------------------------------------

def filter_files(files, extensions):
    if extensions is None:
        return files

    return [
        file for file in files
        if file.suffix.lower() in extensions
    ]


# --------------------------------------------------
# 7. DATE-BASED NAMING
# --------------------------------------------------

def get_file_date(file, date_type):
    try:
        stat = file.stat()

        if date_type == "creation":
            # st_birthtime is available on some platforms.
            # Windows commonly uses st_ctime as creation time.
            timestamp = getattr(
                stat,
                "st_birthtime",
                stat.st_ctime
            )

        else:
            timestamp = stat.st_mtime

        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

    except (OSError, ValueError, OverflowError) as error:
        raise ValueError(
            f"Could not retrieve date for {file.name}: {error}"
        )


# --------------------------------------------------
# 8. GENERATE NEW FILENAMES
# --------------------------------------------------

def generate_filenames(
    files,
    prefix,
    starting_number,
    date_based=False,
    date_type="modification"
):
    rename_plan = []

    for index, file in enumerate(files):
        number = starting_number + index

        if date_based:
            file_date = get_file_date(file, date_type)
            new_name = f"{file_date}_{prefix}_{number:03d}{file.suffix}"

        else:
            new_name = f"{prefix}_{number:03d}{file.suffix}"

        new_path = file.parent / new_name

        rename_plan.append({
            "original": file,
            "new": new_path
        })

    return rename_plan


# --------------------------------------------------
# 9. CHECK FILENAME CONFLICTS
# --------------------------------------------------

def check_conflicts(rename_plan):
    source_paths = {
        str(item["original"].resolve()).lower()
        for item in rename_plan
    }

    target_paths = set()
    conflicts = []

    for item in rename_plan:
        target = item["new"]

        normalized_target = str(target.resolve()).lower()

        # Check duplicate target names
        if normalized_target in target_paths:
            conflicts.append(
                f"Duplicate target filename: {target.name}"
            )
            continue

        target_paths.add(normalized_target)

        # Existing selected source files are allowed because
        # they will first be moved to temporary filenames.
        if (
            target.exists()
            and normalized_target not in source_paths
        ):
            conflicts.append(
                f"Target already exists: {target.name}"
            )

    return conflicts


# --------------------------------------------------
# 10. PREVIEW RENAME OPERATIONS
# --------------------------------------------------

def preview_renaming(rename_plan):
    print("\n========== RENAME PREVIEW ==========")

    for item in rename_plan:
        original = item["original"]
        new = item["new"]

        print(f"{original.name}  --->  {new.name}")

    print("====================================")


# --------------------------------------------------
# 11. RENAME FILES SAFELY
# --------------------------------------------------

def rename_files(rename_plan):
    successful = []
    failed = []

    # First move every source to a unique temporary filename.
    # This avoids collisions between files that are being renamed.
    staged = []

    try:
        for item in rename_plan:
            original = item["original"]

            temp_path = original.parent / (
                f".__bulk_rename_{uuid.uuid4().hex}__"
                f"{original.name}"
            )

            original.rename(temp_path)

            staged.append({
                "original": original,
                "temporary": temp_path,
                "new": item["new"]
            })

    except OSError as error:
        failed.append((original.name, str(error)))

        # Restore files that were successfully staged.
        for item in reversed(staged):
            try:
                item["temporary"].rename(item["original"])
            except OSError as restore_error:
                failed.append(
                    (item["original"].name,
                     f"Restoration failed: {restore_error}")
                )

        # Nothing is finalized if staging fails.
        return successful, failed

    # Finalize the renaming operation.
    for index, item in enumerate(staged):
        try:
            item["temporary"].rename(item["new"])
            successful.append(
                (item["original"].name, item["new"].name)
            )

        except OSError as error:
            failed.append((item["original"].name, str(error)))

            # Restore this file and all files not yet finalized.
            remaining = staged[index:]

            for remaining_item in reversed(remaining):
                temp = remaining_item["temporary"]
                original = remaining_item["original"]

                if temp.exists():
                    try:
                        temp.rename(original)
                    except OSError as restore_error:
                        failed.append(
                            (original.name,
                             f"Restoration failed: {restore_error}")
                        )

            # Stop to avoid further unexpected conflicts.
            break

    return successful, failed


# --------------------------------------------------
# 12. DISPLAY SUMMARY
# --------------------------------------------------

def display_summary(successful, failed):
    print("\n========== RENAME SUMMARY ==========")

    print(f"Successfully renamed: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if successful:
        print("\nSuccessful operations:")

        for old_name, new_name in successful:
            print(f"{old_name} ---> {new_name}")

    if failed:
        print("\nFailed operations:")

        for filename, reason in failed:
            print(f"{filename}: {reason}")

    print("====================================")


# --------------------------------------------------
# 13. MAIN APPLICATION
# --------------------------------------------------

def main():
    print("\n====================================")
    print("       BULK FILE RENAMER")
    print("====================================")

    # Get user input
    folder = get_folder_path()
    prefix = get_prefix()
    starting_number = get_starting_number()
    extensions = get_file_types()

    # Date-based naming option
    date_based = (
        input("\nEnable date-based naming? (yes/no): ")
        .strip().lower()
    )

    use_date = date_based in ("yes", "y")

    date_type = "modification"

    if use_date:
        while True:
            choice = input(
                "Choose date type (creation/modification): "
            ).strip().lower()

            if choice in ("creation", "modification"):
                date_type = choice
                break

            print("Please enter creation or modification.")

    # Scan and filter files
    files = scan_files(folder)
    selected_files = filter_files(files, extensions)

    if not selected_files:
        print("\nNo matching files found.")
        return

    print(f"\nFiles found: {len(files)}")
    print(f"Files selected: {len(selected_files)}")

    # Generate new filenames
    try:
        rename_plan = generate_filenames(
            selected_files,
            prefix,
            starting_number,
            use_date,
            date_type
        )

    except (ValueError, OSError) as error:
        print(f"\nUnable to generate filenames: {error}")
        return

    # Check conflicts
    conflicts = check_conflicts(rename_plan)

    if conflicts:
        print("\nFilename conflicts detected:")

        for conflict in conflicts:
            print(f"- {conflict}")

        print("\nNo files were renamed.")
        return

    # Preview
    preview_renaming(rename_plan)

    # Final confirmation
    confirmation = input(
        "\nDo you want to apply these changes? (yes/no): "
    ).strip().lower()

    if confirmation not in ("yes", "y"):
        print("\nOperation cancelled. No files were renamed.")
        return

    # Perform renaming
    successful, failed = rename_files(rename_plan)

    # Display results
    display_summary(successful, failed)


# --------------------------------------------------
# PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()