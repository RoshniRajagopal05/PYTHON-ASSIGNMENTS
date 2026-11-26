
import json
import logging
from pathlib import Path
from watchdog.observers import Observer

from file_processor import FileProcessor
from file_monitor import FolderEventHandler


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
MONITOR_FOLDER = BASE_DIR / "incoming"
DESTINATION_FOLDER = BASE_DIR / "processed"
LOG_FILE = BASE_DIR / "monitoring.log"


def setup_logging():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def load_config():

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            config = json.load(file)

        categories = config.get("categories")

        if not isinstance(categories, dict) or not categories:
            raise ValueError("Categories must be a non-empty dictionary.")

        for category, extensions in categories.items():

            if not isinstance(category, str) or not category.strip():
                raise ValueError("Category names must be non-empty strings.")

            if not isinstance(extensions, list):
                raise ValueError(
                    f"Extensions for {category} must be a list."
                )

            for extension in extensions:

                if not isinstance(extension, str) or not extension.startswith("."):
                    raise ValueError(
                        f"Invalid extension in category {category}: {extension}"
                    )

        return categories

    except (OSError, json.JSONDecodeError, ValueError) as error:

        logging.error("Configuration error: %s", error)
        raise


def validate_directories():

    if not MONITOR_FOLDER.exists():
        raise FileNotFoundError(
            f"Monitoring folder does not exist: {MONITOR_FOLDER}"
        )

    if not MONITOR_FOLDER.is_dir():
        raise NotADirectoryError(
            f"Monitoring path is not a directory: {MONITOR_FOLDER}"
        )

    # Avoid monitoring the destination or a parent of the destination.
    if (
        MONITOR_FOLDER.resolve() == DESTINATION_FOLDER.resolve()
        or MONITOR_FOLDER.resolve() in DESTINATION_FOLDER.resolve().parents
    ):
        raise ValueError(
            "Destination folder must not be inside the monitored folder."
        )

    DESTINATION_FOLDER.mkdir(parents=True, exist_ok=True)


def main():

    setup_logging()

    print("=" * 50)
    print("   AUTOMATED FOLDER MONITORING SYSTEM")
    print("=" * 50)

    try:

        categories = load_config()
        validate_directories()

        processor = FileProcessor(
            destination_folder=DESTINATION_FOLDER,
            categories=categories
        )

        event_handler = FolderEventHandler(processor)

        observer = Observer()

        observer.schedule(
            event_handler,
            str(MONITOR_FOLDER),
            recursive=False
        )

        observer.start()

        logging.info("Monitoring started: %s", MONITOR_FOLDER)
        logging.info("Destination: %s", DESTINATION_FOLDER)

        print(f"\nMonitoring folder: {MONITOR_FOLDER}")
        print(f"Destination folder: {DESTINATION_FOLDER}")
        print("\nAdd files to the incoming folder.")
        print("Press Ctrl + C to stop monitoring.\n")

        try:

            while observer.is_alive():
                observer.join(timeout=1)

        except KeyboardInterrupt:

            print("\nStopping monitoring...")
            logging.info("User requested monitoring shutdown.")

        finally:

            observer.stop()
            observer.join()

            event_handler.executor.shutdown(
                wait=True,
                cancel_futures=False
            )

            logging.info("Monitoring stopped.")

            print("Monitoring stopped successfully.")

    except Exception as error:

        logging.exception("Application error: %s", error)
        print(f"\nApplication failed: {error}")


if __name__ == "__main__":
    main()
