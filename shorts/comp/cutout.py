import sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
w, h = im.size
key = im.copy()
# Flood-fill the outer white background from every border pixel with a key color
for x in range(0, w, 4):
    for y in (0, h - 1):
        if key.getpixel((x, y)) != (255, 0, 255):
            ImageDraw.floodfill(key, (x, y), (255, 0, 255), thresh=40)
for y in range(0, h, 4):
    for x in (0, w - 1):
        if key.getpixel((x, y)) != (255, 0, 255):
            ImageDraw.floodfill(key, (x, y), (255, 0, 255), thresh=40)
k = np.array(key)
bg = (k[..., 0] == 255) & (k[..., 1] == 0) & (k[..., 2] == 255)
alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
# Slightly shrink and soften the mask edge to remove white halo
alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
rgba = im.convert("RGBA")
rgba.putalpha(alpha)
rgba = rgba.crop(rgba.getbbox())
rgba.save(out)
print(rgba.size)
