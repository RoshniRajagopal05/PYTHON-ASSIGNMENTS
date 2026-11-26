from pathlib import Path
from PIL import Image, ImageOps
import csv


SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".gif",
    ".tiff", ".tif", ".webp"
}


def get_size(size_bytes):
    """Convert bytes into a readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def get_unique_path(path):
    """Avoid overwriting an existing file."""
    if not path.exists():
        return path

    counter = 1

    while True:
        new_path = path.with_name(
            f"{path.stem}_{counter}{path.suffix}"
        )

        if not new_path.exists():
            return new_path

        counter += 1


def validate_folder(folder_path):
    """Validate whether the folder exists."""
    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError("Folder does not exist.")

    if not folder.is_dir():
        raise ValueError("Path is not a directory.")

    return folder


def validate_dimensions(width, height):
    """Validate width and height."""
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive.")

    return width, height


def validate_quality(quality):
    """Validate JPEG quality."""
    if quality < 1 or quality > 95:
        raise ValueError("JPEG quality must be between 1 and 95.")

    return quality


def resize_image(image, width, height):
    """Resize an image while maintaining aspect ratio."""
    return ImageOps.contain(
        image,
        (width, height),
        method=Image.Resampling.LANCZOS
    )


def prepare_for_format(image, output_format):
    """Prepare image mode according to the output format."""

    if output_format == "JPEG":
        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, "white")
            alpha = image.getchannel("A")
            background.paste(image, mask=alpha)
            return background

        if image.mode == "P":
            image = image.convert("RGBA")

            background = Image.new("RGB", image.size, "white")
            background.paste(
                image,
                mask=image.getchannel("A")
            )
            return background

        return image.convert("RGB")

    if output_format == "PNG":
        return image.convert("RGBA") if image.mode not in (
            "RGB", "RGBA"
        ) else image

    return image


def save_image(image, path, output_format, quality):
    """Save an image in the selected format."""
    image = prepare_for_format(image, output_format)

    if output_format == "JPEG":
        image.save(
            path,
            format="JPEG",
            quality=quality,
            optimize=True
        )

    elif output_format == "PNG":
        image.save(
            path,
            format="PNG",
            optimize=True
        )


def process_images(
    input_folder,
    output_folder,
    width,
    height,
    output_format,
    quality,
    generate_thumbnails
):
    input_folder = validate_folder(input_folder)

    output_folder = Path(output_folder)

    resized_folder = output_folder / "resized"
    thumbnail_folder = output_folder / "thumbnails"

    resized_folder.mkdir(parents=True, exist_ok=True)

    if generate_thumbnails:
        thumbnail_folder.mkdir(parents=True, exist_ok=True)

    # Collect input files before processing.
    # This prevents newly created output files from
    # accidentally being included in the same run.
    image_files = [
        file for file in input_folder.iterdir()
        if file.is_file()
        and file.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    report = []

    print("\n========== PROCESSING IMAGES ==========\n")

    if not image_files:
        print("No supported image files found.")

    for file in image_files:

        original_dimensions = "Unknown"
        new_dimensions = "N/A"
        original_size = "N/A"
        new_size = "N/A"
        status = "Failed"
        error_message = ""

        try:
            original_size = get_size(file.stat().st_size)

            with Image.open(file) as img:

                # Correct image orientation using EXIF data.
                img = ImageOps.exif_transpose(img)

                original_dimensions = (
                    f"{img.width}x{img.height}"
                )

                # Load image data before closing the source.
                img.load()

                resized = resize_image(img, width, height)

                new_dimensions = (
                    f"{resized.width}x{resized.height}"
                )

                resized = prepare_for_format(
                    resized, output_format
                )

                output_file = get_unique_path(
                    resized_folder
                    / f"{file.stem}.{output_format.lower()}"
                )

                save_image(
                    resized,
                    output_file,
                    output_format,
                    quality
                )

                new_size = get_size(
                    output_file.stat().st_size
                )

                # Optional thumbnail generation.
                if generate_thumbnails:

                    with Image.open(file) as thumb_img:

                        thumb_img = ImageOps.exif_transpose(
                            thumb_img
                        )

                        thumb_img.load()

                        thumbnail = ImageOps.contain(
                            thumb_img,
                            (200, 200),
                            method=Image.Resampling.LANCZOS
                        )

                        thumbnail = prepare_for_format(
                            thumbnail, output_format
                        )

                        thumbnail_file = get_unique_path(
                            thumbnail_folder
                            / f"{file.stem}.{output_format.lower()}"
                        )

                        save_image(
                            thumbnail,
                            thumbnail_file,
                            output_format,
                            quality
                        )

                status = "Success"

                print(f"Processed: {file.name}")
                print(f"Original: {original_dimensions}")
                print(f"Resized: {new_dimensions}")
                print(f"Original size: {original_size}")
                print(f"New size: {new_size}")
                print(f"Status: {status}")
                print("-" * 40)

        except Exception as error:

            error_message = str(error)

            print(f"Failed: {file.name}")
            print(f"Reason: {error_message}")
            print("-" * 40)

        report.append({
            "File": file.name,
            "Original Dimensions": original_dimensions,
            "New Dimensions": new_dimensions,
            "Original Size": original_size,
            "New Size": new_size,
            "Status": status,
            "Error": error_message
        })

    # Generate processing report.
    output_folder.mkdir(parents=True, exist_ok=True)

    report_file = output_folder / "processing_report.csv"

    with report_file.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        fieldnames = [
            "File",
            "Original Dimensions",
            "New Dimensions",
            "Original Size",
            "New Size",
            "Status",
            "Error"
        ]

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(report)

    successful = sum(
        item["Status"] == "Success"
        for item in report
    )

    failed = sum(
        item["Status"] == "Failed"
        for item in report
    )

    print("\n========== SUMMARY ==========")
    print(f"Total images: {len(report)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Report saved: {report_file}")
    print("============================")


def main():

    print("=" * 50)
    print("          BULK IMAGE RESIZER")
    print("=" * 50)

    try:

        input_folder = input(
            "\nEnter input folder path: "
        ).strip().strip('"')

        output_folder = input(
            "Enter output folder path: "
        ).strip().strip('"')

        width = int(input("Enter target width: "))
        height = int(input("Enter target height: "))

        validate_dimensions(width, height)

        print("\nAvailable output formats:")
        print("1. JPEG")
        print("2. PNG")

        format_choice = input(
            "Select output format (1/2): "
        ).strip()

        if format_choice == "1":
            output_format = "JPEG"

        elif format_choice == "2":
            output_format = "PNG"

        else:
            raise ValueError("Invalid format selection.")

        quality = 85

        if output_format == "JPEG":

            quality = int(
                input("Enter JPEG quality (1-95): ")
            )

            validate_quality(quality)

        thumbnail_choice = input(
            "Generate thumbnails? (yes/no): "
        ).strip().lower()

        generate_thumbnails = (
            thumbnail_choice in ("yes", "y")
        )

        process_images(
            input_folder=input_folder,
            output_folder=output_folder,
            width=width,
            height=height,
            output_format=output_format,
            quality=quality,
            generate_thumbnails=generate_thumbnails
        )

    except ValueError as error:

        print(f"\nInput error: {error}")

    except Exception as error:

        print(f"\nApplication error: {error}")


if __name__ == "__main__":
    main()