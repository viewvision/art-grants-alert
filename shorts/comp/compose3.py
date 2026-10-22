# Composite characters + font-rendered speech bubbles (+ optional comic marks) onto a 1080x1920 background
import json, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

cfg = json.load(open(sys.argv[1]))
W, H = 1080, 1920
FONT = ImageFont.truetype("../fonts/NanumSquareRoundB.ttf", cfg.get("font_size", 46))
MARK_FONT = ImageFont.truetype("../fonts/NanumSquareRoundB.ttf", 110)

bg = Image.open(cfg["bg"]).convert("RGBA").resize((W, H), Image.LANCZOS)
chars = Image.open("chars.png")
ch = cfg["char_h"]
chars = chars.resize((int(chars.width * ch / chars.height), ch), Image.LANCZOS)
cx = (W - chars.width) // 2
cy = cfg["feet_y"] - ch
bg.alpha_composite(chars, (cx, cy))

# Locate each character (left = client, right = architect) from alpha columns
a = np.array(chars.split()[-1]) > 20
cols = np.where(a.any(0))[0]
groups, start = [], cols[0]
for i in range(1, len(cols)):
    if cols[i] != cols[i - 1] + 1:
        groups.append((start, cols[i - 1])); start = cols[i]
groups.append((start, cols[-1]))
who = {}
for name, (x0, x1) in zip(["client", "architect"], groups):
    top = np.where(a[:, x0:x1 + 1].any(1))[0][0]
    who[name] = {"x": cx + (x0 + x1) // 2, "top": cy + top, "w": x1 - x0}

d = ImageDraw.Draw(bg)
OUT, PAD, R = 6, 34, 22
for b in cfg["bubbles"]:
    lines = b["text"].split("\n")
    lh = FONT.size + 14
    tw = max(d.textlength(l, font=FONT) for l in lines)
    bw, bh = int(tw + PAD * 2), int(lh * len(lines) - 14 + PAD * 2)
    x, y = b["x"], b["y"]
    d.rounded_rectangle((x, y, x + bw, y + bh), R, fill="white", outline="black", width=OUT)
    # Tail toward the speaker's head
    tx = min(max(who[b["who"]]["x"] + b.get("tail_dx", 0), x + 50), x + bw - 50)
    tip = (tx + b.get("tip_dx", 0), y + bh + b.get("tail_len", 50))
    poly = [(tx - 26, y + bh - OUT), (tx + 26, y + bh - OUT), tip]
    d.polygon(poly, fill="white")
    d.line([poly[0], tip], fill="black", width=OUT)
    d.line([poly[1], tip], fill="black", width=OUT)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=FONT)
        d.text((x + (bw - lw) / 2, y + PAD + i * lh - 4), l, font=FONT, fill="black")

for m in cfg.get("marks", []):
    p = who[m["who"]]
    mx, my = p["x"] + m["dx"], p["top"] + m["dy"]
    if m["type"] == "sweat":
        s = m.get("size", 44)
        d.polygon([(mx, my - s), (mx - s * 0.55, my + s * 0.15), (mx + s * 0.55, my + s * 0.15)], fill=(150, 205, 240), outline="black")
        d.ellipse((mx - s * 0.58, my - s * 0.25, mx + s * 0.58, my + s * 0.9), fill=(150, 205, 240), outline="black", width=5)
        d.polygon([(mx, my - s + 8), (mx - s * 0.45, my + s * 0.1), (mx + s * 0.45, my + s * 0.1)], fill=(150, 205, 240))
        d.line([(mx, my - s), (mx - s * 0.52, my + s * 0.05)], fill="black", width=5)
        d.line([(mx, my - s), (mx + s * 0.52, my + s * 0.05)], fill="black", width=5)
    elif m["type"] == "text":
        f = ImageFont.truetype("../fonts/NanumSquareRoundB.ttf", m.get("size", 110))
        d.text((mx, my), m["text"], font=f, fill=m.get("color", "black"), stroke_width=6, stroke_fill="white", anchor="mm")

bg.convert("RGB").save(cfg["out"], quality=92)
print(cfg["out"], who)
