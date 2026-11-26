
import logging
import shutil
import time
from pathlib import Path
from threading import Lock


class FileProcessor:

    def __init__(self, destination_folder, categories):
        self.destination_folder = Path(destination_folder)
        self.categories = categories

        # Tracks files currently being processed.
        self.processing_files = set()
        self.lock = Lock()

    def get_category(self, file_path):

        extension = file_path.suffix.lower()

        for category, extensions in self.categories.items():
            normalized_extensions = [
                ext.lower() for ext in extensions
            ]

            if extension in normalized_extensions:
                return category

        return None

    def wait_for_file(self, file_path, checks=3, delay=1, timeout=60):

        start_time = time.time()
        previous_size = None
        stable_count = 0

        while time.time() - start_time < timeout:

            try:

                if not file_path.exists():
                    time.sleep(delay)
                    continue

                current_size = file_path.stat().st_size

                if current_size == previous_size:
                    stable_count += 1
                else:
                    stable_count = 0

                previous_size = current_size

                if stable_count >= checks:
                    return True

            except OSError:
                stable_count = 0
                previous_size = None

            time.sleep(delay)

        raise TimeoutError(
            f"File did not become stable: {file_path.name}"
        )

    def get_unique_destination(self, destination):

        if not destination.exists():
            return destination

        counter = 1

        while True:

            new_destination = destination.with_name(
                f"{destination.stem}_{counter}{destination.suffix}"
            )

            if not new_destination.exists():
                return new_destination

            counter += 1

    def process_file(self, file_path):

        file_path = Path(file_path)

        try:
            file_key = str(file_path.resolve())

        except OSError:
            file_key = str(file_path)

        with self.lock:

            if file_key in self.processing_files:
                return

            self.processing_files.add(file_key)

        try:

            if not file_path.exists() or not file_path.is_file():
                return

            category = self.get_category(file_path)

            if category is None:

                logging.info(
                    "Unsupported file type: %s",
                    file_path.name
                )

                print(f"Unsupported file: {file_path.name}")
                return

            self.wait_for_file(file_path)

            category_folder = self.destination_folder / category
            category_folder.mkdir(parents=True, exist_ok=True)

            destination = category_folder / file_path.name
            destination = self.get_unique_destination(destination)

            # Retry moving the file if Windows temporarily locks it.
            for attempt in range(5):

                try:
                    shutil.move(str(file_path), str(destination))
                    break

                except PermissionError:

                    if attempt == 4:
                        raise

                    logging.warning(
                        "File is locked. Retrying move (%s/5): %s",
                        attempt + 1,
                        file_path.name
                    )

                    time.sleep(2)

            logging.info(
                "Successfully processed: %s -> %s",
                file_path.name,
                destination
            )

            print(f"Processed successfully: {file_path.name}")
            print(f"Destination: {destination}")
            print(
                f"Notification: {file_path.name} "
                "has been organized!"
            )

        except Exception as error:

            logging.exception(
                "Failed to process %s",
                file_path.name
            )

            print(f"Failed to process {file_path.name}: {error}")

        finally:

            # Allow the same source path to be processed again
            # when a new file is added later.
            with self.lock:
                self.processing_files.discard(file_key)
