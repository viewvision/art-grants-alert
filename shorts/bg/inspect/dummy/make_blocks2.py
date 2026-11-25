"""Block-mannequin layout v2 (per user notes)."""
import math, importlib.util
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location('mb', 'bg/inspect/dummy/make_blocks.py')
src = open('bg/inspect/dummy/make_blocks.py').read().split('jobs = [')[0]
ns = {}; exec(src, ns)
rbox, limb, head, beam, label = ns['rbox'], ns['limb'], ns['head'], ns['beam'], ns['label']
FILL, LINE = ns['FILL'], ns['LINE']
WOOD = (170, 120, 70, 210)

ALU = (205, 210, 215, 235)
def ladder(d, x, y_top, y_bot, w_top=230, w_bot=420, splay=330, rung=230):
    """A-frame step ladder seen in 3/4: front section with rungs + rear legs splayed back."""
    def bar(x0, y0, x1, y1, t=26):
        ang = math.atan2(y1 - y0, x1 - x0) + math.pi/2; dx, dy = t*math.cos(ang), t*math.sin(ang)
        d.polygon([(x0-dx, y0-dy), (x0+dx, y0+dy), (x1+dx, y1+dy), (x1-dx, y1-dy)], fill=ALU, outline=LINE, width=5)
    # rear legs (behind)
    bar(x - w_top/2 + 40, y_top, x - w_bot/2 + splay, y_bot - 120); bar(x + w_top/2 + 40, y_top, x + w_bot/2 + splay, y_bot - 120)
    # front rails
    bar(x - w_top/2, y_top, x - w_bot/2, y_bot); bar(x + w_top/2, y_top, x + w_bot/2, y_bot)
    n = int((y_bot - y_top) // rung)
    for i in range(1, n + 1):
        y = y_top + i * (y_bot - y_top) / (n + 1); t = (y - y_top) / (y_bot - y_top)
        half = (w_top + (w_bot - w_top) * t) / 2
        d.rectangle((x - half, y - 22, x + half, y + 22), fill=ALU, outline=LINE, width=5)
    d.rectangle((x - w_top/2 - 20, y_top - 40, x + w_top/2 + 60, y_top + 10), fill=(150, 155, 160, 240), outline=LINE, width=5)  # top cap
    for xx in (x - w_bot/2, x + w_bot/2): d.rectangle((xx - 34, y_bot - 10, xx + 34, y_bot + 30), fill=(30, 30, 30, 255))  # feet

def s1():
    bg = Image.open('bg/B7_int_ceiling_post_topaz2x.jpg').convert('RGBA')
    lay = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    hole_bottom = 1150                                     # lower edge of the big ceiling hole
    ladder(d, 1370, 1900, 3350)
    hx, hy = 1370, 1760                                    # hip
    limb(d, hx - 70, hy, 360, 4, 120); limb(d, hx + 70, hy, 260, -6, 120)   # legs standing on upper steps
    rbox(d, hx, (hy + hole_bottom) / 2, 360, hy - hole_bottom, 0)            # torso disappears into hole
    limb(d, hx - 200, 1300, 220, 175, 85)                 # arm going up into the hole
    # hide anything above the hole edge (upper body is inside the ceiling)
    lay.paste((0, 0, 0, 0), (1150, 0, 1620, hole_bottom))
    bg.alpha_composite(lay); label(bg, '① 천장 속: 사다리 위, 가슴 위로 천장 안에 넣고 봄'); return bg

def s2():
    bg = Image.open('bg/inspect/insp2_floor_wide.jpg').convert('RGBA')
    lay = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, base = 560, 2200                                   # back view, crouching, facing the crack (up in frame)
    limb(d, cx - 110, base - 230, 250, 35, 95); limb(d, cx + 110, base - 230, 250, -35, 95)   # folded legs splayed
    rbox(d, cx - 170, base - 10, 120, 60, 0); rbox(d, cx + 170, base - 10, 120, 60, 0)        # feet
    rbox(d, cx, base - 420, 330, 390, 0)                   # back (torso seen from behind, leaning forward)
    head(d, cx, base - 690, 120)                           # back of head, looking down at the crack
    limb(d, cx + 150, base - 560, 220, -20, 65)            # one arm reaching forward (seen from behind)
    beam(lay, cx + 180, base - 380, 800, 1230, 0.2)        # flashlight toward the crack
    bg.alpha_composite(lay); label(bg, '② 바닥: 쪼그려 앉아 들여다보는 뒷모습'); return bg

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
