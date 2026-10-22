# Build mouthless character layers + aligned mouth-shape sprites (transparent PNG) from the pose image
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

S = 3                      # working scale vs. source image
SS = 4                     # supersampling for smooth mouth strokes
src = Image.open("src_pose.png").convert("RGB")

CHARS = {
    # crop box in source px, mouth box to erase, fill color sample point, mouth center, base width, line px
    "client":    dict(crop=(170, 100, 440, 640), erase=(282, 213, 310, 235), fill=(215, 175, 160), center=(299.0, 224.5), w=17, lw=2.6, inner=(120, 50, 55)),
    "architect": dict(crop=(570, 30, 900, 640), erase=(755, 220, 785, 229), fill=(770, 236), center=(769.5, 224.5), w=23, lw=3.0, inner=(95, 40, 35)),
}

def cutout(im):
    """Transparent background: flood-fill white from the borders only, so inner whites survive."""
    key = im.copy()
    KEY = (255, 0, 255)
    w, h = key.size
    for x in range(0, w, 3):
        for y in (0, h - 1):
            if key.getpixel((x, y)) != KEY:
                ImageDraw.floodfill(key, (x, y), KEY, thresh=45)
    for y in range(0, h, 3):
        for x in (0, w - 1):
            if key.getpixel((x, y)) != KEY:
                ImageDraw.floodfill(key, (x, y), KEY, thresh=45)
    k = np.array(key).astype(int)
    a = np.where((k[..., 0] == 255) & (k[..., 1] == 0) & (k[..., 2] == 255), 0, 255).astype(np.uint8)
    alpha = Image.fromarray(a).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out

def mouth_layer(size, c, kind):
    """Draw one mouth shape on a transparent full-size canvas (coords already in output px)."""
    W, H = size
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    cx, cy = c["mx"] * SS, c["my"] * SS
    lw = int(c["lw"] * S * SS)
    hw = c["w"] * S * SS / 2
    ink = (25, 20, 20, 255)
    inner = c["inner"] + (255,)
    if kind == 0:      # closed: flat line
        d.line([(cx - hw, cy), (cx + hw, cy)], fill=ink, width=lw)
        r = lw / 2
        for x in (cx - hw, cx + hw):
            d.ellipse((x - r, cy - r, x + r, cy + r), fill=ink)
    else:
        rx, ry = {1: (hw * 0.75, hw * 0.28), 2: (hw * 0.9, hw * 0.62), 3: (hw * 0.42, hw * 0.5)}[kind]
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=inner, outline=ink, width=lw)
    return big.resize((W, H), Image.LANCZOS)

for name, c in CHARS.items():
    x0, y0, x1, y1 = c["crop"]
    crop = src.crop(c["crop"])
    # erase original mouth with the face fill color
    d = ImageDraw.Draw(crop)
    fill = c["fill"] if len(c["fill"]) == 3 and c["fill"][0] > 100 else src.getpixel(c["fill"])
    ex0, ey0, ex1, ey1 = c["erase"]
    # inpaint the original mouth: mask = non-face-colored pixels inside the mouth box
    import cv2
    a = np.array(crop)
    bx0, by0, bx1, by1 = ex0 - x0, ey0 - y0, ex1 - x0, ey1 - y0
    mask = np.zeros(a.shape[:2], np.uint8)
    reg = a[by0:by1 + 1, bx0:bx1 + 1].astype(int)
    mask[by0:by1 + 1, bx0:bx1 + 1] = (np.abs(reg - np.array(fill)).sum(2) > 45) * 255
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
    a = cv2.inpaint(a, mask, 4, cv2.INPAINT_TELEA)
    crop = Image.fromarray(a)
    crop = crop.resize((crop.width * S, crop.height * S), Image.LANCZOS)
    body = cutout(crop)
    body.save(f"{name}_body_nomouth.png")
    c["mx"] = (c["center"][0] - x0) * S
    c["my"] = (c["center"][1] - y0) * S
    for k, label in enumerate(["closed", "small", "wide", "o"]):
        mouth_layer(body.size, c, k).save(f"{name}_mouth_{k}_{label}.png")
    print(name, body.size)
