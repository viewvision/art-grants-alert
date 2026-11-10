"""「우리의 인상」 체험 스토리보드 — 6컷, 미니멀 (흑백 라인 + 화면 속만 컬러).

컷: WAIT 대기 / STAND 서기 / IMPRINT 새겨지기 / FLOW 흐르기 / BLEND 스며들기 / 110 DAYS 축적
글꼴: 영문·숫자 = Arial 계열(Liberation Sans) Bold, 한글 = WenQuanYi Zen Hei.
실행: python3 fig_storyboard.py → fig_storyboard.png
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

LATIN_BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
ARIAL_BOLD = '/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf'
KOREAN     = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
if os.path.exists(ARIAL_BOLD):
    LATIN_BOLD = ARIAL_BOLD

_cache = {}
def font(path, size):
    if (path, size) not in _cache:
        _cache[(path, size)] = ImageFont.truetype(path, size)
    return _cache[(path, size)]

def is_korean(ch):
    o = ord(ch)
    return (0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F
            or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF)

def runs(text):
    out = []
    for ch in text:
        k = is_korean(ch) if ch != ' ' else (out[-1][1] if out else False)
        if out and out[-1][1] == k:
            out[-1][0] += ch
        else:
            out.append([ch, k])
    return out

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
DARK  = (70, 70, 70)
MID   = (140, 140, 140)
LIGHT = (210, 210, 210)

def hx(h, a=255):
    return tuple(bytes.fromhex(h)) + (a,)

CYAN, LAV, CORAL, AMBER, VIOLET, AQUA = '49D2E3', 'C2A9F0', 'F8825A', 'E7B258', '9A72EB', '96E2EC'

W, H = 2200, 1380
img = Image.new('RGBA', (W, H), WHITE + (255,))
d = ImageDraw.Draw(img)

def width(text, size, dr=None):
    dr = dr or d
    return sum(dr.textlength(t, font=font(KOREAN if k else LATIN_BOLD, size)) for t, k in runs(text))

def T(x, y, text, size, fill, align='left', dr=None):
    dr = dr or d
    if align == 'center':
        x -= width(text, size, dr) / 2
    base = y + size * 0.82
    for t, k in runs(text):
        fnt = font(KOREAN if k else LATIN_BOLD, size)
        dr.text((x, base), t, font=fnt, fill=fill, anchor='ls')
        x += dr.textlength(t, font=fnt)

# ── 라인 인물 (아이소메트릭과 같은 손그림 라인)
_rng = random.Random(11)
STAND = [(-0.08, 0), (-0.09, 0.30), (-0.11, 0.47), (-0.16, 0.46), (-0.16, 0.66),
         (-0.12, 0.79), (-0.04, 0.82), (0.04, 0.82), (0.12, 0.79), (0.16, 0.66),
         (0.16, 0.46), (0.11, 0.47), (0.09, 0.30), (0.08, 0), (0.02, 0), (0.0, 0.40),
         (-0.02, 0)]
WALK = [(-0.13, 0), (-0.08, 0.30), (-0.10, 0.47), (-0.15, 0.48), (-0.15, 0.66),
        (-0.12, 0.79), (-0.04, 0.82), (0.04, 0.82), (0.12, 0.79), (0.15, 0.66),
        (0.14, 0.47), (0.10, 0.47), (0.10, 0.30), (0.16, 0), (0.08, 0), (0.02, 0.36),
        (-0.05, 0)]

def chaikin(pts, n=3):
    for _ in range(n):
        out = []
        for i in range(len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1),
                    (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = out
    return pts

def jit(pts, a):
    return [(x + _rng.uniform(-a, a), y + _rng.uniform(-a, a)) for x, y in pts]

def person_shape(fx, fy, h, pose=STAND):
    body = [(fx + u * h * 1.15, fy - v * h) for u, v in pose]
    head = [(fx + 0.045 * h * 1.15 * math.cos(t), fy - (0.905 + 0.058 * math.sin(t)) * h)
            for t in [i * 2 * math.pi / 12 for i in range(12)]]
    return body, head

def line_person(dr, fx, fy, h, pose=STAND, color=BLACK, w=2, fill=WHITE):
    body, head = person_shape(fx, fy, h, pose)
    if fill:
        dr.polygon(chaikin(body), fill=fill)
        dr.polygon(chaikin(head), fill=fill)
    for k, a in enumerate([1.6, 1.1]):
        c = color if k == 0 else (color[0], color[1], color[2], 110)
        for shape in (body, head):
            p = chaikin(jit(shape, a))
            dr.line(p + [p[0]], fill=c, width=w if k == 0 else 1, joint='curve')

# ── 화면 속 내용 (컬러, 부드럽게 번진 면)
def screen_img(w, h, blobs, figure=None, text=None, blur=28):
    """blobs: [(cx, cy, rx, ry, hex, alpha)] (0~1 비율). figure: (색 목록, 알파, 흐림, 퍼짐)."""
    base = Image.new('RGBA', (w, h), (252, 251, 249, 255))
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for cx, cy, rx, ry, col, a in blobs:
        ld.ellipse([(cx - rx) * w, (cy - ry) * h, (cx + rx) * w, (cy + ry) * h], fill=hx(col, a))
    base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))
    if figure:
        cols, a, fb, spread = figure
        fl = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fl)
        fh = h * 0.78
        body, head = person_shape(w * 0.5, h * 0.97, fh)
        fd.polygon(chaikin(body), fill=hx(cols[0], a))
        fd.polygon(chaikin(head), fill=hx(cols[0], a))
        if len(cols) > 1:   # 두 번째 원소색을 아래쪽에 겹침
            fd.polygon(chaikin([(x, max(y, h * 0.55)) for x, y in body]), fill=hx(cols[1], int(a * 0.8)))
        if spread:          # 스며들기: 바깥으로 번짐
            for k in range(6):
                ang = k * math.pi / 3
                fd.ellipse([w * (0.5 + 0.22 * math.cos(ang)) - 40, h * (0.55 + 0.18 * math.sin(ang)) - 30,
                            w * (0.5 + 0.22 * math.cos(ang)) + 40, h * (0.55 + 0.18 * math.sin(ang)) + 30],
                           fill=hx(cols[k % len(cols)], int(a * 0.5)))
        base.alpha_composite(fl.filter(ImageFilter.GaussianBlur(fb)))
    if text:
        sd = ImageDraw.Draw(base)
        T(w / 2, h * 0.08, text, 15, (90, 90, 90), 'center', sd)
    return base

BG_BLOBS = [(0.22, 0.45, 0.30, 0.45, CYAN, 120), (0.35, 0.65, 0.25, 0.35, LAV, 110),
            (0.78, 0.45, 0.30, 0.45, CORAL, 110), (0.68, 0.70, 0.25, 0.30, AMBER, 110)]
SIL_OUTLINE = (None,)

# ── 컷 하나 그리기
FW, FH = 620, 420          # 컷 크기
SCW, SCH = 360, 270        # 화면 크기 (4:3)

def frame(x, y, key, desc, scr, person=None, extra=None):
    d.rectangle([x, y, x + FW, y + FH], outline=LIGHT, width=2)
    floor = y + FH - 48
    d.line([(x + 30, floor), (x + FW - 30, floor)], fill=BLACK, width=2)
    sx, sy = x + (FW - SCW) // 2, floor - 54 - SCH
    if scr is not None:
        img.alpha_composite(scr, (sx, sy))
        d.rectangle([sx, sy, sx + SCW, sy + SCH], outline=BLACK, width=2)
        # 카메라 · 프로젝터
        d.rectangle([sx + SCW // 2 - 18, sy - 14, sx + SCW // 2 + 18, sy - 4], fill=BLACK)
        d.rectangle([sx + SCW // 2 - 26, floor - 12, sx + SCW // 2 + 26, floor], fill=BLACK)
    if extra:
        extra(sx, sy, floor)
    if person:
        px, pose, *rest = person
        line_person(d, x + px, floor, 230, pose, fill=(rest[0] if rest else None))
    T(x, y + FH + 18, key, 26, BLACK)
    T(x + width(key, 26) + 14, y + FH + 22, desc, 20, DARK)

# ── 제목
M = 80
T(M, 58, 'STORYBOARD', 24, MID)
T(M, 96, '「우리의 인상」 — 한 사람의 1분, 그리고 110일', 44, BLACK)
T(M, 162, '서서, 새기고, 남기다 — 떠난 사람의 색이 쌓여 다음 사람이 마주하는 화면이 된다', 22, DARK)

GX = [M, M + FW + 50, M + 2 * (FW + 50)]
GY = [250, 250 + FH + 110]

# 1 WAIT — 축적 화면만 흐름
frame(GX[0], GY[0], 'WAIT', '아무도 없을 때, 쌓인 인상들이 흐른다',
      screen_img(SCW, SCH, BG_BLOBS))

# 2 STAND — 표시 위치에 선다
def spot(sx, sy, floor):
    cx = sx + SCW // 2
    d.ellipse([cx - 70, floor - 8, cx + 70, floor + 8], outline=BLACK, width=2)
frame(GX[1], GY[0], 'STAND', '표시 위치에 서면 실루엣이 나타난다',
      screen_img(SCW, SCH, BG_BLOBS, figure=([ 'FFFFFF'], 200, 6, False)),
      person=(FW // 2, STAND), extra=spot)

# 3 IMPRINT — 색이 맺힌다
frame(GX[2], GY[0], 'IMPRINT', '3~5초, 내 감정의 색이 맺힌다',
      screen_img(SCW, SCH, BG_BLOBS, figure=([CORAL, AMBER], 220, 5, False)),
      person=(FW // 2, STAND), extra=spot)

# 4 FLOW — 움직임을 따라 흐르고, 비춰주는 문장
def motion(sx, sy, floor):
    for k in range(3):
        yy = sy + 120 + k * 26
        d.line([(sx + SCW // 2 + 60, yy), (sx + SCW // 2 + 110, yy)], fill=(255, 255, 255, 230), width=3)
frame(GX[0], GY[1], 'FLOW', '움직이면 색이 따라 흐르고, 한 문장이 비춘다',
      screen_img(SCW, SCH, BG_BLOBS, figure=([CORAL, AMBER], 220, 9, False), text='조금 흔들리고 있네요.'),
      person=(FW // 2 + 20, STAND), extra=spot)

# 5 BLEND — 떠나면 색이 스며들고, 질문이 남는다
frame(GX[1], GY[1], 'BLEND', '떠나면 색이 화면에 스미고, 질문이 남는다',
      screen_img(SCW, SCH, BG_BLOBS, figure=([CORAL, AMBER], 150, 22, True), text='이 흔들림은 누구에게 닿을까요?'),
      person=(FW - 70, WALK, WHITE))

# 6 110 DAYS — Day 1 → 30 → 110
def days(x, y):
    d.rectangle([x, y, x + FW, y + FH], outline=LIGHT, width=2)
    mw, mh = 172, 129
    gap = (FW - 3 * mw) // 4
    states = [
        ('Day 1',   [(0.5, 0.6, 0.15, 0.2, CYAN, 70)]),
        ('Day 30',  [(0.3, 0.5, 0.25, 0.35, CYAN, 110), (0.7, 0.55, 0.25, 0.35, CORAL, 100),
                     (0.5, 0.7, 0.2, 0.25, LAV, 90)]),
        ('Day 110', BG_BLOBS + [(0.5, 0.4, 0.3, 0.3, VIOLET, 80), (0.15, 0.8, 0.2, 0.2, AQUA, 110),
                                (0.85, 0.25, 0.2, 0.2, AMBER, 110)]),
    ]
    for i, (lab, blobs) in enumerate(states):
        mx = x + gap + i * (mw + gap)
        my = y + 120
        img.alpha_composite(screen_img(mw, mh, blobs, blur=14), (mx, my))
        d.rectangle([mx, my, mx + mw, my + mh], outline=BLACK, width=2)
        T(mx + mw / 2, my + mh + 18, lab, 22, BLACK, 'center')
        if i < 2:
            T(mx + mw + gap / 2, my + mh / 2 - 12, '→', 22, MID, 'center')
    T(x + FW / 2, y + 50, 'Accumulated — 지워지지 않고 겹겹이 스민다', 20, DARK, 'center')
    T(x, y + FH + 18, '110 DAYS', 26, BLACK)
    T(x + width('110 DAYS', 26) + 14, y + FH + 22, '한 사람의 색이 모여 우리의 인상이 된다', 20, DARK)
days(GX[2], GY[1])

# 컷 사이 흐름 표시
for gy in GY:
    for gx in GX[:2]:
        T(gx + FW + 25, gy + FH / 2 - 14, '→', 26, MID, 'center')

T(M, H - 64, 'One visit ≈ 1 min · No touch · 얼굴 영상은 저장하지 않는다', 20, MID)

img.convert('RGB').save('fig_storyboard.png')
print('saved fig_storyboard.png')
