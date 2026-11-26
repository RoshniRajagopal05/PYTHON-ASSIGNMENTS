from pathlib import Path
from PIL import Image

folder = Path("test_images")
folder.mkdir(exist_ok=True)

# Create landscape image
Image.new("RGB", (1920, 1080), "skyblue").save(
    folder / "landscape.jpg"
)

# Create portrait image
Image.new("RGB", (1080, 1920), "pink").save(
    folder / "portrait.png"
)

# Create square image
Image.new("RGB", (1000, 1000), "lightgreen").save(
    folder / "square.jpg"
)

print("Test images created successfully!")