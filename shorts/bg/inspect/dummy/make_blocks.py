"""Block-mannequin layout (round head + box torso + box limbs) on inspection backgrounds."""
import math
from PIL import Image, ImageDraw, ImageFont
F = 'fonts/NanumSquareRoundB.ttf'
FILL = (255, 205, 0, 170); LINE = (20, 20, 20, 255); BEAM = (255, 250, 200, 110)

def rbox(d, cx, cy, w, h, ang):
    """rectangle centred at (cx,cy), size w x h, rotated ang degrees (0 = upright)."""
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    pts = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
    d.polygon([(cx + x*c - y*s, cy + x*s + y*c) for x, y in pts], fill=FILL, outline=LINE, width=8)
def limb(d, x0, y0, length, ang, w=70):
    """box from (x0,y0) going in direction ang (0 = down, 90 = left...), returns end point."""
    a = math.radians(ang); ex, ey = x0 - length*math.sin(a), y0 + length*math.cos(a)
    rbox(d, (x0+ex)/2, (y0+ey)/2, w, length, ang); return ex, ey
def head(d, cx, cy, r):
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=FILL, outline=LINE, width=8)
def beam(layer, x, y, tx, ty, spread=0.18):
    d = ImageDraw.Draw(layer); ang = math.atan2(ty-y, tx-x); L = math.hypot(tx-x, ty-y)
    p1 = (x + L*math.cos(ang+spread), y + L*math.sin(ang+spread)); p2 = (x + L*math.cos(ang-spread), y + L*math.sin(ang-spread))
    d.polygon([(x, y), p1, p2], fill=BEAM)
def label(img, text):
    d = ImageDraw.Draw(img); f = ImageFont.truetype(F, 50); w = d.textlength(text, font=f)
    d.rounded_rectangle((40, 40, 90 + w, 130), 26, fill=(255, 255, 255, 235), outline=LINE, width=4)
    d.text((65, 58), text, font=f, fill=LINE)

def scene(bgfile, draw_fn, text):
    bg = Image.open('bg/inspect/' + bgfile).convert('RGBA')
    lay = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    draw_fn(lay, d); bg.alpha_composite(lay); label(bg, text); return bg

# ① ceiling (looking up): figure cut off at the bottom, seen from below, arm up with flashlight into the hole
def s1(lay, d):
    beam(lay, 420, 1700, 560, 700, 0.22)
    rbox(d, 760, 2450, 520, 700, -4)            # torso (cropped by frame bottom)
    head(d, 780, 1950, 190)                     # head tilted back
    ex, ey = limb(d, 560, 2200, 300, 160, 90)   # upper arm up-left
    limb(d, ex, ey, 260, 175, 80)               # forearm up, flashlight at end
    rbox(d, 440, 1720, 60, 160, 15)             # flashlight
# ② floor oblique: crouching lower-left, flashlight toward the crack
def s2(lay, d):
    hx, hy = 430, 2330                                   # hip
    kx, ky = limb(d, hx, hy, 300, -80, 105)              # thigh forward
    limb(d, kx, ky, 300, 8, 95)                          # shin down
    sx, sy = hx + 0.57*430, hy - 0.82*430                # shoulder (torso leaning forward-right)
    rbox(d, (hx+sx)/2, (hy+sy)/2, 270, 430, 35)          # torso
    head(d, sx + 0.57*170, sy - 0.82*170, 140)
    ex, ey = limb(d, sx, sy, 250, -55, 80)               # upper arm forward-down
    fx, fy = limb(d, ex, ey, 190, -35, 72)               # forearm
    rbox(d, fx + 40, fy + 15, 55, 140, -60)              # flashlight
    beam(lay, fx + 70, fy + 30, 1180, 1700, 0.2)
# ③ wall: bending forward on the right, face close to the crack, hand on wall
def s3(lay, d):
    hx, hy = 1180, 1900                                  # hip
    limb(d, hx - 50, hy, 680, 3, 110); limb(d, hx + 60, hy, 680, -3, 110)   # legs
    sx, sy = hx - 0.87*520, hy - 0.5*520                 # shoulder (bent toward wall)
    rbox(d, (hx+sx)/2, (hy+sy)/2, 300, 520, -60)         # torso
    head(d, sx - 0.87*160, sy - 0.5*160, 150)
    ex, ey = limb(d, sx, sy, 260, 70, 78)                # arm reaching to wall
    limb(d, ex, ey, 170, 95, 72)
    beam(lay, sx - 0.87*160 - 120, sy - 0.5*160, 700, 1250, 0.15)
# ④ corner: standing, looking up, one arm reaching up to the corner
def s4(lay, d):
    rbox(d, 820, 2050, 340, 620, 0)             # torso
    head(d, 840, 1620, 160)                     # head tilted up
    limb(d, 760, 2350, 520, 0, 110); limb(d, 890, 2350, 520, 0, 110)  # legs
    ex, ey = limb(d, 950, 1800, 330, 200, 80)   # arm up-right toward corner
    limb(d, ex, ey, 260, 195, 75)
    limb(d, 690, 1800, 380, 10, 80)             # other arm down
    beam(lay, 870, 1500, 1360, 420, 0.12)       # gaze line to corner

jobs = [('insp1_ceiling.jpg', s1, '① 천장 속: 아래에서 올려다보며 손전등'),
        ('insp2_floor_angle.jpg', s2, '② 바닥: 쪼그려 앉아 균열 비춤'),
        ('insp3_wall.jpg', s3, '③ 벽: 숙여서 균열 들여다봄, 손은 벽'),
        ('insp4_corner.jpg', s4, '④ 모서리: 올려다보며 팔 뻗음')]
small = []
for bgf, fn, txt in jobs:
    im = scene(bgf, fn, txt).convert('RGB')
    im.save('bg/inspect/dummy/block_' + bgf, quality=90); small.append(im.resize((384, 688)))
sheet = Image.new('RGB', (384*4 + 30, 688), 'white')
for i, s in enumerate(small): sheet.paste(s, (i*394, 0))
sheet.save('bg/inspect/dummy/block_all.jpg', quality=88); print('ok')
