# Highlight steel beams/columns with an orange glow; everything else slightly dimmed
import sys
from PIL import Image, ImageFilter, ImageChops
import numpy as np

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
W, H = im.size
a = np.array(im).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
luma = (r + g + b) / 3

# Hand-traced steel members (coords for a 1152x2048 frame), intersected with the bluish-grey steel color
from PIL import ImageDraw
sx, sy = W / 1152, H / 2048
polys = [[(0, 234), (1152, 228), (1152, 358), (0, 364)],
         [(0, 563), (1152, 561), (1152, 636), (0, 640)],
         [(150, 706), (990, 706), (990, 772), (150, 772)],
         [(235, 812), (925, 812), (925, 860), (235, 860)],
         [(80, 600), (172, 600), (172, 1372), (80, 1372)],
         [(985, 590), (1062, 590), (1062, 1362), (985, 1362)]]
pm = Image.new("L", (W, H), 0)
pd = ImageDraw.Draw(pm)
for poly in polys:
    pd.polygon([(x * sx, y * sy) for x, y in poly], fill=255)
region = np.array(pm) > 0
color = Image.fromarray((((b - r > 2) & (luma < 140)) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(15))
steel = region & (np.array(color) > 0)

m = Image.fromarray((steel * 255).astype(np.uint8))
m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))   # close small gaps
m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))   # drop specks
core = m.filter(ImageFilter.GaussianBlur(1.5))
glow = m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(28))

ORANGE = (255, 122, 28)
dim = Image.blend(im, Image.new("RGB", im.size, (0, 0, 0)), 0.28)
lit = Image.composite(im, dim, glow.point(lambda v: min(255, v * 2)))
orange = Image.new("RGB", im.size, ORANGE)
tinted = ImageChops.overlay(lit, orange)
tinted = Image.blend(tinted, orange, 0.25)
res = Image.composite(tinted, lit, core)
halo = ImageChops.screen(res, Image.composite(orange, Image.new("RGB", im.size), glow.point(lambda v: int(v * 0.55))))
halo.save(out, quality=95)
m.save(out.rsplit(".", 1)[0] + "_mask.png")
