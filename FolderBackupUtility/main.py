import json
import logging
import shutil
import zipfile

from pathlib import Path
from datetime import datetime


# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "backup.log"


# ==================================================
# LOGGING
# ==================================================

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ],
        force=True
    )


# ==================================================
# CONFIGURATION MANAGEMENT
# ==================================================

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        logging.error("Configuration file not found.")
        return None

    except json.JSONDecodeError:
        logging.error("Invalid JSON configuration.")
        return None


# ==================================================
# DIRECTORY VALIDATION
# ==================================================

def validate_directories(source, destination):

    source = Path(source).expanduser().resolve()
    destination = Path(destination).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(
            f"Source directory does not exist: {source}"
        )

    if not source.is_dir():
        raise NotADirectoryError(
            f"Source path is not a directory: {source}"
        )

    if source == destination:
        raise ValueError(
            "Source and backup destination cannot be the same."
        )

    if destination.exists() and not destination.is_dir():
        raise NotADirectoryError(
            "Backup destination is not a directory."
        )

    destination.mkdir(parents=True, exist_ok=True)

    return source, destination


# ==================================================
# BACKUP FILE COLLECTION
# ==================================================

def collect_files(source, destination):

    files = []

    for item in source.rglob("*"):

        resolved_item = item.resolve()

        # Exclude the backup destination from the source.
        try:
            resolved_item.relative_to(destination)
            continue

        except ValueError:
            pass

        # Avoid archiving symbolic links.
        if item.is_symlink():
            continue

        if item.is_file():
            files.append(item)

    return files


# ==================================================
# BACKUP CREATION
# ==================================================

def create_backup(source, destination):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

    backup_name = f"backup_{timestamp}.zip"

    backup_path = destination / backup_name

    logging.info("Starting backup.")

    files = collect_files(source, destination)

    try:

        with zipfile.ZipFile(
            backup_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED
        ) as archive:

            # Include empty directories.
            for directory in source.rglob("*"):

                if directory.is_symlink():
                    continue

                if not directory.is_dir():
                    continue

                resolved_directory = directory.resolve()

                try:
                    resolved_directory.relative_to(destination)
                    continue

                except ValueError:
                    pass

                if not any(directory.iterdir()):

                    archive.write(
                        directory,
                        directory.relative_to(source).as_posix() + "/"
                    )

            # Include files.
            for file_path in files:

                archive.write(
                    file_path,
                    file_path.relative_to(source).as_posix()
                )

        # Verify the archive before considering it successful.
        with zipfile.ZipFile(backup_path, "r") as archive:

            corrupted_file = archive.testzip()

            if corrupted_file is not None:

                raise zipfile.BadZipFile(
                    f"Corrupted file detected: {corrupted_file}"
                )

        logging.info(
            "Backup successfully created and verified: %s",
            backup_path
        )

        return backup_path

    except Exception:

        if backup_path.exists():
            backup_path.unlink()

        logging.exception("Backup creation failed.")

        raise


# ==================================================
# RETENTION MANAGEMENT
# ==================================================

def manage_retention(destination, max_backups):

    if max_backups < 1:
        raise ValueError(
            "Retention limit must be at least 1."
        )

    backups = sorted(
        destination.glob("backup_*.zip"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    old_backups = backups[max_backups:]

    for backup in old_backups:

        try:

            backup.unlink()

            logging.info(
                "Removed older backup: %s",
                backup.name
            )

        except OSError:

            logging.exception(
                "Unable to remove backup: %s",
                backup.name
            )


# ==================================================
# BACKUP PROCESS
# ==================================================

def run_backup(source, destination, max_backups):

    source, destination = validate_directories(
        source,
        destination
    )

    backup_path = create_backup(
        source,
        destination
    )

    # Retention runs only after backup creation and verification.
    manage_retention(
        destination,
        max_backups
    )

    return backup_path


# ==================================================
# MAIN
# ==================================================

def main():

    setup_logging()

    print("=" * 50)
    print("          FOLDER BACKUP UTILITY")
    print("=" * 50)

    config = load_config()

    if config is None:
        return

    default_source = config.get("source_folder", "")
    default_destination = config.get("backup_folder", "backups")
    default_retention = config.get("max_backups", 5)

    source_input = input(
        f"Enter source folder [{default_source}]: "
    ).strip()

    source = source_input or default_source

    destination_input = input(
        f"Enter backup destination [{default_destination}]: "
    ).strip()

    destination = destination_input or default_destination

    retention_input = input(
        f"Enter maximum backups to retain [{default_retention}]: "
    ).strip()

    try:

        max_backups = (
            int(retention_input)
            if retention_input
            else int(default_retention)
        )

        if max_backups < 1:
            raise ValueError(
                "Retention limit must be at least 1."
            )

        if not source:
            raise ValueError(
                "Source directory must be specified."
            )

        backup_path = run_backup(
            source,
            destination,
            max_backups
        )

        print("\nBackup completed successfully!")

        print(f"Backup file: {backup_path}")

    except ValueError as error:

        logging.error("Input error: %s", error)

        print(f"\nInput error: {error}")

    except FileNotFoundError as error:

        logging.error("Directory error: %s", error)

        print(f"\nDirectory error: {error}")

    except PermissionError as error:

        logging.error("Permission error: %s", error)

        print(f"\nPermission error: {error}")

    except OSError as error:

        logging.exception("Operating system error.")

        print(f"\nBackup failed: {error}")

    except Exception as error:

        logging.exception("Unexpected error.")

        print(f"\nUnexpected error: {error}")


if __name__ == "__main__":
    main()