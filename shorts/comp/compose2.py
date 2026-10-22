# Composite characters (with soft ground shadows) and bubbles onto a 1080x1920 background
import sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

bg_path, out = sys.argv[1], sys.argv[2]
char_h = int(sys.argv[3])      # character height in px
feet_y = int(sys.argv[4])      # ground line in px
W, H = 1080, 1920

bg = Image.open(bg_path).convert("RGBA").resize((W, H), Image.LANCZOS)
chars = Image.open("chars.png")
s = char_h / chars.height
chars = chars.resize((int(chars.width * s), char_h), Image.LANCZOS)
cx = (W - chars.width) // 2
cy = feet_y - chars.height

# Soft shadow: one blurred ellipse per character, found from alpha column groups
a = np.array(chars.split()[-1]) > 20
cols = np.where(a.any(0))[0]
groups, start = [], cols[0]
for i in range(1, len(cols)):
    if cols[i] != cols[i - 1] + 1:
        groups.append((start, cols[i - 1])); start = cols[i]
groups.append((start, cols[-1]))
shadow = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(shadow)
for x0, x1 in groups:
    mx, rw = cx + (x0 + x1) / 2, (x1 - x0) * 0.62
    d.ellipse((mx - rw, feet_y - rw * 0.16, mx + rw, feet_y + rw * 0.16), fill=150)
    d.ellipse((mx - rw * 0.45, feet_y - rw * 0.07, mx + rw * 0.45, feet_y + rw * 0.07), fill=230)
shadow = shadow.filter(ImageFilter.GaussianBlur(char_h * 0.018))
dark = Image.new("RGBA", (W, H), (25, 22, 20, 0))
dark.putalpha(shadow.point(lambda v: int(v * 0.55)))
bg.alpha_composite(dark)
bg.alpha_composite(chars, (cx, cy))

# Bubbles above the heads
b = Image.open("bubbles.png")
bw = int(W * 0.94)
b = b.resize((bw, int(b.height * bw / b.width)), Image.LANCZOS)
bg.alpha_composite(b, ((W - bw) // 2, max(40, cy - b.height - 10)))
bg.convert("RGB").save(out, quality=92)
