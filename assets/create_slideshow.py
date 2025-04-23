from PIL import Image
import glob
import os

# Create a new directory for the slideshow if it doesn't exist
slideshow_dir = "visualization_slideshow"
if not os.path.exists(slideshow_dir):
    os.makedirs(slideshow_dir)

# Collect all PNG images from directories that exist
all_images = []

# Check directories that actually have images
image_dirs = [
    "fig/about_dataset_diagram",
    "fig/adjusted_system_design_final"
    # The other directories don't have PNG files
]

for dir_path in image_dirs:
    if os.path.exists(dir_path):
        image_files = glob.glob(f"{dir_path}/*.png")
        print(f"Looking for PNGs in {dir_path}: found {len(image_files)} files")

        for img_path in image_files:
            print(f"Found image: {img_path}")
            all_images.append(img_path)

# Sort images to ensure consistent order
all_images.sort()

# If we have images, create the GIF
if len(all_images) == 0:
    print("No images found! Check your directory paths.")
else:
    # Open all images
    print(f"Loading {len(all_images)} images...")
    images = [Image.open(image) for image in all_images]

    # Standardize image sizes (use the size of the first image)
    base_width, base_height = images[0].size
    for i in range(1, len(images)):
        images[i] = images[i].resize((base_width, base_height), Image.LANCZOS)

    # Save as animated GIF
    output_path = os.path.join(slideshow_dir, "visualization_slideshow.gif")
    print(f"Creating GIF with {len(images)} images, 2-second duration per frame...")

    # Make sure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=2000,  # milliseconds
        loop=0  # 0 means loop forever
    )
    print(f"GIF created successfully: {output_path}")

    # Print markdown for README
    print("\nAdd this to your README.md:")
    print("```markdown")
    print(f"![Project Visualization Summary]({output_path})")
    print("```")