
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


class FolderEventHandler(FileSystemEventHandler):

    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.executor = ThreadPoolExecutor(max_workers=4)

    def on_created(self, event):

        if event.is_directory:
            return

        file_path = Path(event.src_path)

        print(f"\nNew file detected: {file_path.name}")

        # Process files in a separate worker thread.
        self.executor.submit(
            self.processor.process_file,
            file_path
        )

    def on_moved(self, event):

        if event.is_directory:
            return

        # Handle files moved into the monitored directory.
        file_path = Path(event.dest_path)

        print(f"\nFile moved into monitored folder: {file_path.name}")

        self.executor.submit(
            self.processor.process_file,
            file_path
        )
