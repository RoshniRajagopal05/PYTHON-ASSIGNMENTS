from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from main import move_files


with TemporaryDirectory() as temp_folder:

    # Create a temporary test directory
    directory = Path(temp_folder)

    # Create the destination folder
    images_folder = directory / "Images"
    images_folder.mkdir()

    # Create a sample source file
    source_file = directory / "photo.jpg"
    source_file.write_text("Sample image content")

    # Prepare the categorised files
    categorised_files = {
        "Images": [source_file]
    }

    print("Testing file movement error handling...")

    # Simulate a permission error during file movement
    with patch(
        "main.shutil.move",
        side_effect=PermissionError("Access denied!")
    ):

        summary, failed_files = move_files(
            categorised_files,
            directory
        )

    # Verify the results
    print("\n========== TEST RESULTS ==========")

    print("Successful movements:", summary["Images"])
    print("Failed movements:", len(failed_files))
    print("Failure reason:", failed_files[0]["error"])

    print(
        "Original file still exists:",
        source_file.exists()
    )

    # Automatically verify expected behaviour
    assert summary["Images"] == 0
    assert len(failed_files) == 1
    assert source_file.exists()

    print("\nTEST PASSED!")