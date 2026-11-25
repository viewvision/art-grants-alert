"""Rough dummy composites: existing architect frames keyed out and placed on inspection backgrounds."""
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = 'fonts/NanumSquareRoundB.ttf'
def frame(video, t):
    c = cv2.VideoCapture(video); c.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, f = c.read()
    rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
    a = 255 - np.clip((rgb.min(2).astype(int) - 225) * 9, 0, 255).astype(np.uint8)  # white -> transparent
    im = Image.fromarray(np.dstack([rgb, a]))
    return im.crop(im.getbbox())
def place(bg, ch, h, x, y, flip=False, shadow=True):
    if flip: ch = ch.transpose(Image.FLIP_LEFT_RIGHT)
    ch = ch.resize((int(ch.width * h / ch.height), h), Image.LANCZOS)
    if shadow:
        sh = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
        d.ellipse((x - ch.width * 0.45, y - 18, x + ch.width * 0.45, y + 18), fill=(0, 0, 0, 110))
        bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    bg.alpha_composite(ch, (int(x - ch.width / 2), int(y - ch.height)))
def label(bg, text):
    d = ImageDraw.Draw(bg); f = ImageFont.truetype(F, 46)
    w = d.textlength(text, font=f)
    d.rounded_rectangle((40, 40, 80 + w, 120), 24, fill=(255, 255, 255, 230), outline=(20, 20, 20), width=4)
    d.text((60, 55), text, font=f, fill=(20, 20, 20))
L = 'lipsync_ltx/final/'
up = frame(L + 'c4_architect_05_1080.mp4', 1.6)        # pointing up
chin = frame(L + 'c3_architect_03_1080.mp4', 2.0)     # hand on chin, looking up
arm = frame(L + 'c1_architect_01_1080.mp4', 2.5)      # arm extended

jobs = [
    ('insp1_ceiling.jpg', up, 1500, 520, 2700, False, '① 천장 속: 손전등 들고 올려다봄 (임시 포즈)'),
    ('insp2_floor_angle.jpg', chin, 1150, 420, 2650, False, '② 바닥: 쪼그려 앉아 손전등 (임시 포즈)'),
    ('insp3_wall.jpg', chin, 1650, 1150, 2720, True, '③ 벽: 숙여서 균열 들여다봄 (임시 포즈)'),
    ('insp4_corner.jpg', arm, 1450, 980, 2700, True, '④ 모서리: 팔 뻗어 짚으며 올려다봄 (임시 포즈)'),
]
outs = []
for bgf, ch, h, x, y, flip, txt in jobs:
    bg = Image.open('bg/inspect/' + bgf).convert('RGBA')
    place(bg, ch, h, x, y, flip)
    label(bg, txt)
    out = 'bg/inspect/dummy/dummy_' + bgf
    bg.convert('RGB').save(out, quality=90); outs.append(bg.convert('RGB').resize((384, 688)))
sheet = Image.new('RGB', (384 * 4 + 30, 688), 'white')
for i, o in enumerate(outs): sheet.paste(o, (i * 394, 0))
sheet.save('bg/inspect/dummy/dummy_all.jpg', quality=88)
print('ok')
