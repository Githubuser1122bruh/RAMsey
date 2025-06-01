from PIL import Image
from rembg import remove

input_path = "/Users/samhithpola/Documents/GitHub/RAMsey/LeftRightHeadRemoveBG.png"
image = Image.open(input_path)
no_bg = remove(image)

width, height = no_bg.size


bbox = no_bg.getbbox() 
left, top, right, bottom = bbox

content_mid_y = (top + bottom) // 2

top_half = no_bg.crop((0, top, width, content_mid_y))
bottom_half = no_bg.crop((0, content_mid_y, width, bottom))

def crop_to_drawing(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img

top_cropped = crop_to_drawing(top_half)
bottom_cropped = crop_to_drawing(bottom_half)

# Save output
top_cropped.save("head_top.png")
bottom_cropped.save("head_bottom.png")
