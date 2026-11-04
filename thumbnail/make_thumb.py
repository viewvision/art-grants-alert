# YouTube thumbnail (1280x720): photo on the right, headline block on the left in the brand orange
import json, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT_DIR = "../shorts/fonts/"
EB = FONT_DIR + "NanumSquareEB.ttf"
B = FONT_DIR + "NanumSquareB.ttf"
ORANGE = (217, 89, 2)
INK = (18, 20, 24)
W, H = 1280, 720

cfg = json.load(open(sys.argv[1]))
canvas = Image.new("RGB", (W, H), INK)

# Photo panel on the right, fading into the dark left side
src = Image.open(cfg["photo"]).convert("RGB").crop(tuple(cfg["crop"]))
pw = cfg.get("photo_w", 780)
src = src.resize((pw, int(src.height * pw / src.width)), Image.LANCZOS)
src = ImageEnhance.Contrast(src).enhance(1.08)
top = (H - src.height) // 2 + cfg.get("photo_dy", 0)
canvas.paste(src, (W - pw, top))
fade = Image.new("L", (W, H), 0)
fd = ImageDraw.Draw(fade)
x0 = W - pw
for i in range(260):
    fd.line([(x0 + i, 0), (x0 + i, H)], fill=int(255 * (1 - i / 260) ** 1.6))
fd.rectangle((0, 0, x0, H), fill=255)
canvas = Image.composite(Image.new("RGB", (W, H), INK), canvas, fade)

d = ImageDraw.Draw(canvas)
L = 64

def fit(text, font_path, size, maxw):
    f = ImageFont.truetype(font_path, size)
    while d.textlength(text, font=f) > maxw and size > 20:
        size -= 2
        f = ImageFont.truetype(font_path, size)
    return f

# Series label + part pill
lab = ImageFont.truetype(B, 30)
d.text((L, 58), cfg["label"], font=lab, fill=(235, 235, 235))
pf = ImageFont.truetype(EB, 28)
pt = cfg["part"]
pw2 = d.textlength(pt, font=pf)
d.rounded_rectangle((L, 112, L + pw2 + 36, 158), 23, fill=ORANGE)
d.text((L + 18, 118), pt, font=pf, fill="white")

# Headline lines; "hl": true lines sit on an orange bar
y = cfg.get("head_y", 210)
for line in cfg["head"]:
    f = fit(line["t"], EB, line.get("size", 86), cfg.get("head_maxw", 600))
    tw = d.textlength(line["t"], font=f)
    if line.get("hl"):
        d.rectangle((L - 10, y - 4, L + tw + 14, y + f.size + 14), fill=ORANGE)
    d.text((L, y), line["t"], font=f, fill="white", stroke_width=0)
    y += f.size + cfg.get("gap", 22)

# Sub copy
sf = fit(cfg["sub"], B, 30, 600)
d.text((L, y + 18), cfg["sub"], font=sf, fill=(205, 205, 205))

# Footer
ff = ImageFont.truetype(B, 22)
d.text((L, H - 58), cfg.get("footer", "서울특별시건축사회"), font=ff, fill=(160, 160, 160))
canvas.save(cfg["out"], quality=95)
print(cfg["out"])
