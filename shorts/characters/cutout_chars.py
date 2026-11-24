# Clean transparent cutouts of each base character (no bubbles, no grey floor shadows)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

im = Image.open("base_reference.png").convert("RGB")
crop = im.crop((560, 560, 1320, 1420))           # below the speech bubbles
w, h = crop.size
key = crop.copy(); K = (255, 0, 255)
for x in range(0, w, 3):
    for y in (0, h - 1):
        if key.getpixel((x, y)) != K: ImageDraw.floodfill(key, (x, y), K, thresh=45)
for y in range(0, h, 3):
    for x in (0, w - 1):
        if key.getpixel((x, y)) != K: ImageDraw.floodfill(key, (x, y), K, thresh=45)
k = np.array(key).astype(int); px = np.array(crop).astype(int)
a = np.where((k[..., 0] == 255) & (k[..., 1] == 0) & (k[..., 2] == 255), 0, 255).astype(np.uint8)
yy = np.arange(h)[:, None]
grey = (np.ptp(px, axis=2) < 14) & (px.min(2) > 110) & (yy > 700)   # floor shadow ellipses
a[grey] = 0
alpha = Image.fromarray(a).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
rgba = crop.convert("RGBA"); rgba.putalpha(alpha)
rgba = rgba.crop(rgba.getbbox()); rgba.save("both_cutout.png")
# split at the empty column between the two figures
al = np.array(rgba.split()[-1]) > 20
cols = np.where(al.any(0))[0]
gaps = [c for c in range(cols[0], cols[-1]) if not al[:, c].any()]
mid = gaps[len(gaps) // 2]
for name, box in (("client", (0, 0, mid, rgba.height)), ("architect", (mid, 0, rgba.width, rgba.height))):
    p = rgba.crop(box); p = p.crop(p.getbbox()); p.save(f"{name}_base.png"); print(name, p.size)
