"""Block-mannequin layout v2 (per user notes)."""
import math, importlib.util
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location('mb', 'bg/inspect/dummy/make_blocks.py')
src = open('bg/inspect/dummy/make_blocks.py').read().split('jobs = [')[0]
ns = {}; exec(src, ns)
rbox, limb, head, beam, label = ns['rbox'], ns['limb'], ns['head'], ns['beam'], ns['label']
FILL, LINE = ns['FILL'], ns['LINE']
WOOD = (170, 120, 70, 210)

def ladder(d, x, y_top, y_bot, w=330, rung=200):
    for xx in (x - w/2, x + w/2):
        d.rectangle((xx - 22, y_top, xx + 22, y_bot), fill=WOOD, outline=LINE, width=6)
    y = y_bot - 150
    while y > y_top + 60:
        d.rectangle((x - w/2, y - 14, x + w/2, y + 14), fill=WOOD, outline=LINE, width=5); y -= rung

def s1():
    bg = Image.open('bg/B7_int_ceiling_post_topaz2x.jpg').convert('RGBA')
    lay = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    hole_bottom = 1150                                     # lower edge of the big ceiling hole
    ladder(d, 1370, hole_bottom - 40, 3350)
    hx, hy = 1370, 1760                                    # hip
    limb(d, hx - 70, hy, 520, 4, 120); limb(d, hx + 70, hy, 420, -6, 120)   # legs on rungs
    rbox(d, hx, (hy + hole_bottom) / 2, 360, hy - hole_bottom, 0)            # torso disappears into hole
    limb(d, hx - 200, 1300, 220, 175, 85)                 # arm going up into the hole
    # hide anything above the hole edge (upper body is inside the ceiling)
    lay.paste((0, 0, 0, 0), (1150, 0, 1620, hole_bottom))
    bg.alpha_composite(lay); label(bg, '① 천장 속: 사다리 위, 가슴 위로 천장 안에 넣고 봄'); return bg

def s2():
    bg = Image.open('bg/inspect/insp2_floor_wide.jpg').convert('RGBA')
    lay = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    hx, hy = 430, 1820
    kx, ky = limb(d, hx, hy, 200, -80, 70); limb(d, kx, ky, 200, 8, 65)
    sx, sy = hx + 0.6*290, hy - 0.8*290
    rbox(d, (hx+sx)/2, (hy+sy)/2, 185, 290, 37)
    head(d, sx + 0.6*110, sy - 0.8*110, 95)
    ex, ey = limb(d, sx, sy, 170, -60, 55); fx, fy = limb(d, ex, ey, 130, -40, 50)
    rbox(d, fx + 25, fy + 10, 38, 95, -60)
    beam(lay, fx + 45, fy + 20, 790, 1220, 0.2)
    bg.alpha_composite(lay); label(bg, '② 바닥: 쪼그려 앉아 자세히 봄'); return bg

def s3():
    bg = Image.open('bg/inspect/insp3_wall.jpg').convert('RGBA')
    lay = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # back view, standing close to the wall, leaning slightly toward the crack
    limb(d, 1000, 2000, 700, 2, 130); limb(d, 1180, 2000, 700, -2, 130)     # legs
    rbox(d, 1080, 1650, 430, 720, -10)                     # torso from behind (leaning left)
    head(d, 990, 1180, 175)                                # back of head, close to the crack
    ex, ey = limb(d, 900, 1400, 300, 150, 90)              # arm up to the wall next to crack
    limb(d, ex, ey, 180, 165, 80)
    bg.alpha_composite(lay); label(bg, '③ 벽: 벽 틈을 들여다보는 뒷모습'); return bg

def s4():
    bg = Image.open('bg/inspect/insp4_corner.jpg').convert('RGBA')
    lay = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rbox(d, 880, 2080, 330, 600, 0)
    head(d, 870, 1660, 155)
    limb(d, 810, 2370, 480, 0, 110); limb(d, 950, 2370, 480, 0, 110)
    ex, ey = limb(d, 760, 1840, 300, 165, 80); fx, fy = limb(d, ex, ey, 230, 172, 75)   # arm up holding flashlight
    rbox(d, fx - 10, fy - 50, 55, 140, 172)
    beam(lay, fx - 15, fy - 110, 760, 840, 0.14)           # light into the ceiling-wall gap
    bg.alpha_composite(lay); label(bg, '④ 모서리: 천장·벽 틈을 손전등으로 봄'); return bg

outs = []
for name, fn in [('b2_ceiling', s1), ('b2_floor', s2), ('b2_wall', s3), ('b2_corner', s4)]:
    im = fn().convert('RGB'); im.save(f'bg/inspect/dummy/{name}.jpg', quality=90)
    outs.append(im.resize((384, int(im.height * 384 / im.width))))
H = max(o.height for o in outs); sheet = Image.new('RGB', (384*4 + 30, H), 'white')
for i, o in enumerate(outs): sheet.paste(o, (i*394, 0))
sheet.save('bg/inspect/dummy/b2_all.jpg', quality=88); print('ok')
