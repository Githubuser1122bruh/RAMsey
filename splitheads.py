from PIL import Image
from rembg import remove

# Load image and remove background
input_path = "/Users/samhithpola/Documents/GitHub/RAMsey/LeftRightHeadRemoveBG.png"
image = Image.open(input_path)
no_bg = remove(image)

# Get dimensions
width, height = no_bg.size

# Split top and bottom
# Step 1: Get bounding box of drawing
bbox = no_bg.getbbox()  # (left, top, right, bottom)
left, top, right, bottom = bbox

# Step 2: Calculate content midpoint
content_mid_y = (top + bottom) // 2

# Step 3: Crop based on drawing content, not full image
top_half = no_bg.crop((0, top, width, content_mid_y))
bottom_half = no_bg.crop((0, content_mid_y, width, bottom))

# Function to crop transparent parts
def crop_to_drawing(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img

# Auto-crop both halves
top_cropped = crop_to_drawing(top_half)
bottom_cropped = crop_to_drawing(bottom_half)

# Save output
top_cropped.save("head_top.png")
bottom_cropped.save("head_bottom.png")
