# Split the character reference into a transparent bubbles layer and a characters layer (flat shadows removed)
import sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

src = sys.argv[1]
im = Image.open(src).convert("RGB")
w, h = im.size
key = im.copy()
KEY = (255, 0, 255)
for x in range(0, w, 4):
    for y in (0, h - 1):
        if key.getpixel((x, y)) != KEY:
            ImageDraw.floodfill(key, (x, y), KEY, thresh=40)
for y in range(0, h, 4):
    for x in (0, w - 1):
        if key.getpixel((x, y)) != KEY:
            ImageDraw.floodfill(key, (x, y), KEY, thresh=40)
k = np.array(key).astype(int)
a = np.where((k[..., 0] == 255) & (k[..., 1] == 0) & (k[..., 2] == 255), 0, 255).astype(np.uint8)

# Drop the flat grey ground ellipses under the feet
px = np.array(im).astype(int)
yy = np.arange(h)[:, None]
grey = (np.ptp(px, axis=2) < 12) & (px.min(2) > 120) & (yy > 640)
a[grey] = 0

alpha = Image.fromarray(a).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
rgba = im.convert("RGBA")
rgba.putalpha(alpha)

bubbles = rgba.crop((0, 0, w, 290))
chars = rgba.crop((0, 290, w, h))
bubbles.crop(bubbles.getbbox()).save("bubbles.png")
chars.crop(chars.getbbox()).save("chars.png")
print(Image.open("bubbles.png").size, Image.open("chars.png").size)
