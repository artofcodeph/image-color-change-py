from PIL import Image
import numpy as np

# Load the image
img = Image.open("input.webp").convert("RGBA")
arr = np.array(img)

# Split channels
r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]

# Mask the red area (tuned for your image)
mask = (r > 150) & (g < 100) & (b < 100)

# New color: #A5CF53
arr[mask, 0:3] = [0xA5, 0xCF, 0x53]

# Save result
Image.fromarray(arr).save("output.png")
