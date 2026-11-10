"""「우리의 인상」 설치 아이소메트릭 — 미니멀 버전 (흑백·그레이).

단위는 미터. x = 벽을 따라(폭), y = 벽에서 관람객 쪽(깊이), z = 높이.
글꼴: 영문·숫자·기호 = Arial 계열(Liberation Sans, Arial과 글자 폭 동일) Bold,
      한글 = WenQuanYi Zen Hei (Arial에는 한글 글리프가 없음).
실행: python3 fig_iso_install.py → fig_iso_install.png
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

LATIN_BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
ARIAL_BOLD = '/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf'   # 있으면 우선 사용
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
            or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF or o == 0x33A1)

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
LIGHT = (200, 200, 200)
PALE  = (236, 236, 236)

# ── 공간 치수 (m)
ZW, ZD, WH = 3.2, 3.2, 2.6          # 구역 폭·깊이, 벽 높이
DX0, DX1 = 0.265, 2.935             # 투사 화면 폭 약 2.67m (4:3)
DZ0, DZ1 = 0.40, 2.40               # 투사 화면 높이 2.0m
STAND = (1.6, 1.2)                  # 체험 위치 (화면에서 1.2m)

W, H = 2200, 1620
S = 210
OX, OY = 1040, 800
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))

def P(x, y, z=0.0):
    return (OX + (x - y) * C30 * S, OY + (x + y) * S30 * S - z * S)

img = Image.new('RGBA', (W, H), WHITE + (255,))
d = ImageDraw.Draw(img, 'RGBA')

def width(text, size):
    return sum(d.textlength(t, font=font(KOREAN if k else LATIN_BOLD, size)) for t, k in runs(text))

def T(x, y, text, size, fill, align='left'):
    """y = 글자 윗선. 영문(Bold)과 한글을 한 기준선 위에 이어서 그린다."""
    if align == 'center':
        x -= width(text, size) / 2
    elif align == 'right':
        x -= width(text, size)
    base = y + size * 0.82
    for t, k in runs(text):
        fnt = font(KOREAN if k else LATIN_BOLD, size)
        d.text((x, base), t, font=fnt, fill=fill, anchor='ls')
        x += d.textlength(t, font=fnt)

def poly(pts, fill=None, outline=BLACK, width_=2):
    q = [P(*p) for p in pts]
    if fill:
        d.polygon(q, fill=fill)
    if outline:
        d.line(q + [q[0]], fill=outline, width=width_)

def dashed(a, b, color=MID, w=2, dash=12, gap=9):
    (x0, y0), (x1, y1) = P(*a), P(*b)
    L = math.hypot(x1 - x0, y1 - y0)
    n = int(L // (dash + gap)) + 1
    for i in range(n):
        t0 = i * (dash + gap) / L
        t1 = min((i * (dash + gap) + dash) / L, 1)
        if t0 >= 1:
            break
        d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=color, width=w)

def leader(pt3, txt_xy, key, desc):
    px, py = P(*pt3)
    d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=BLACK)
    d.line([(px, py), txt_xy], fill=LIGHT, width=2)
    tx, ty = txt_xy
    right = tx < px
    xk = tx - 10 if right else tx + 10
    T(xk, ty - 16, key, 24, BLACK, 'right' if right else 'left')
    T(xk, ty + 16, desc, 20, DARK, 'right' if right else 'left')

# ── 헤더
M = 80
T(M, 58, 'INSTALLATION', 24, MID)
T(M, 96, '「우리의 인상」 — 설치 (안)', 44, BLACK)
T(M, 162, 'Floor 3.2 × 3.2m · 10㎡ 이내 · Wall Projection · 장비 규격은 협의 전 예시값', 22, DARK)

# ── 바닥
poly([(0, 0, 0), (ZW, 0, 0), (ZW, ZD, 0), (0, ZD, 0)], fill=(248, 248, 248), width_=2)
# 관람·대기 영역 (체험 위치 뒤) — 옅은 사선
for k in range(1, 16):
    t = k / 16
    dashed((t * ZW, 2.0, 0), (t * ZW, ZD, 0), color=LIGHT, w=1, dash=5, gap=8)
dashed((0, 2.0, 0), (ZW, 2.0, 0), color=MID, w=2)

# ── 벽 (뒤·왼쪽)
poly([(0, 0, 0), (ZW, 0, 0), (ZW, 0, WH), (0, 0, WH)], fill=(228, 228, 228))
poly([(0, 0, 0), (0, ZD, 0), (0, ZD, WH), (0, 0, WH)], fill=(214, 214, 214))

# ── 투사 화면 — 겹겹이 스민 인상(회색 톤)
cx = (DX0 + DX1) / 2
d.polygon([P(DX0, 0, DZ0), P(DX1, 0, DZ0), P(DX1, 0, DZ1), P(DX0, 0, DZ1)], fill=WHITE)

# ── 러프한 라인 인물 (건축 스케일 인물 스케치 느낌: 외곽선만, 살짝 흔들리는 선)
import random
_rng = random.Random(7)

# 정규화 좌표: u = 좌우(키 대비), v = 높이(0 바닥 ~ 1 머리 끝)
# 포즈별 몸 외곽선 (머리 제외)
POSES = {
    'stand': [(-0.08, 0), (-0.09, 0.30), (-0.11, 0.47), (-0.16, 0.46), (-0.16, 0.66),
              (-0.12, 0.79), (-0.04, 0.82), (0.04, 0.82), (0.12, 0.79), (0.16, 0.66),
              (0.16, 0.46), (0.11, 0.47), (0.09, 0.30), (0.08, 0), (0.02, 0), (0.0, 0.40),
              (-0.02, 0)],
    'coat':  [(-0.12, 0), (-0.13, 0.35), (-0.15, 0.62), (-0.11, 0.79), (-0.04, 0.82),
              (0.04, 0.82), (0.11, 0.79), (0.15, 0.62), (0.13, 0.35), (0.12, 0),
              (0.03, 0), (0.0, 0.12), (-0.03, 0)],
    'slim':  [(-0.06, 0), (-0.07, 0.40), (-0.10, 0.62), (-0.09, 0.78), (-0.03, 0.82),
              (0.03, 0.82), (0.09, 0.78), (0.10, 0.62), (0.07, 0.40), (0.06, 0),
              (0.015, 0), (0.0, 0.42), (-0.015, 0)],
}
ARM_NOTCH = {'stand': [((-0.115, 0.66), (-0.11, 0.50)), ((0.115, 0.66), (0.11, 0.50))],
             'coat': [((-0.10, 0.68), (-0.10, 0.48)), ((0.10, 0.68), (0.10, 0.48))],
             'slim': []}

def _jit(pts, amt):
    return [(x + _rng.uniform(-amt, amt), y + _rng.uniform(-amt, amt)) for x, y in pts]

def _chaikin(pts, n=3, closed=True):
    """모서리를 둥글린다 — 손으로 그은 듯한 유기적인 외곽선."""
    for _ in range(n):
        out = []
        m = len(pts) if closed else len(pts) - 1
        for i in range(m):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1),
                    (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = out
    return pts

def _stroke(draw, pts, color, w, closed=True):
    pts = _chaikin(pts, 3, closed)
    seq = pts + [pts[0]] if closed else pts
    draw.line(seq, fill=color, width=w, joint='curve')

def sketch_person(to_screen, pose, color, w=2, fill=None, jit=2.2, draw=None):
    """to_screen(u, v) → 화면 좌표. 몸 외곽선 + 머리 타원 + 팔 구분선을 두 번 겹쳐 그린다."""
    draw = draw or d
    body = [to_screen(u, v) for u, v in POSES[pose]]
    head = [to_screen(0.045 * math.cos(t), 0.905 + 0.058 * math.sin(t))
            for t in [i * 2 * math.pi / 12 for i in range(12)]]
    if fill:
        draw.polygon(_chaikin(body), fill=fill)
        draw.polygon(_chaikin(head), fill=fill)
    for k in range(2):                       # 두 번 그어 손그림 느낌
        a = jit if k == 0 else jit * 0.7
        c = color if k == 0 else color[:3] + (110,) if len(color) == 4 else color + (110,)
        _stroke(draw, _jit(body, a), c, w if k == 0 else max(1, w - 1))
        _stroke(draw, _jit(head, a * 0.6), c, w if k == 0 else max(1, w - 1))
        for (u0, v0), (u1, v1) in ARM_NOTCH[pose]:
            if k == 0:
                draw.line(_jit([to_screen(u0, v0), to_screen(u1, v1)], a), fill=c, width=max(1, w - 1))

def wall_person(xc, zb, hgt, pose, color, w):
    sketch_person(lambda u, v: P(xc + u * hgt, 0, zb + v * hgt), pose, color, w)

# 앞서 다녀간 사람들(회색) + 지금 선 사람(검정)
for xc, hg, pose in [(0.62, 1.45, 'coat'), (1.02, 1.35, 'slim'), (2.12, 1.50, 'stand'), (2.52, 1.40, 'coat')]:
    wall_person(xc, DZ0 + 0.06, hg, pose, (150, 150, 150), 2)
wall_person(cx, DZ0 + 0.06, 1.62, 'stand', (20, 20, 20), 3)
poly([(DX0, 0, DZ0), (DX1, 0, DZ0), (DX1, 0, DZ1), (DX0, 0, DZ1)], fill=None, outline=BLACK, width_=2)

# ── 초단초점 프로젝터 (벽 하단 바닥)
PX0, PX1, PY0, PY1, PZ = cx - 0.25, cx + 0.25, 0.06, 0.36, 0.12
poly([(PX0, PY1, 0), (PX1, PY1, 0), (PX1, PY1, PZ), (PX0, PY1, PZ)], fill=(50, 50, 50))
poly([(PX1, PY0, 0), (PX1, PY1, 0), (PX1, PY1, PZ), (PX1, PY0, PZ)], fill=(30, 30, 30))
poly([(PX0, PY0, PZ), (PX1, PY0, PZ), (PX1, PY1, PZ), (PX0, PY1, PZ)], fill=(80, 80, 80))
for tx in [DX0, DX1]:
    dashed((cx, PY0 + 0.05, PZ), (tx, 0, DZ1), color=LIGHT, w=1)

# ── 스피커 2조
for sxp in [0.13, 3.07]:
    poly([(sxp - 0.08, 0, 2.08), (sxp + 0.08, 0, 2.08), (sxp + 0.08, 0, 2.42), (sxp - 0.08, 0, 2.42)],
         fill=BLACK, outline=BLACK, width_=1)
    hx, hy = P(sxp, 0, 2.2)
    d.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], outline=(150, 150, 150), width=2)

# ── 깊이 카메라
poly([(cx - 0.13, 0, DZ1 + 0.04), (cx + 0.13, 0, DZ1 + 0.04),
      (cx + 0.13, 0, DZ1 + 0.14), (cx - 0.13, 0, DZ1 + 0.14)], fill=BLACK, width_=1)
sx, sy = STAND
for tgt in [(sx - 0.9, sy + 0.5, 0), (sx + 0.9, sy + 0.5, 0)]:
    dashed((cx, 0.02, DZ1 + 0.04), tgt, color=MID, w=1)

# ── 체험 위치
ring = [P(sx + 0.35 * math.cos(t), sy + 0.35 * math.sin(t), 0)
        for t in [i * 2 * math.pi / 64 for i in range(64)]]
d.line(ring + [ring[0]], fill=BLACK, width=2)

# ── 관람객 (1.65m) — 라인 인물, 흰 면으로 뒤 선을 가림
fx, fy = P(sx, sy, 0)
hpx = 1.65 * S
sketch_person(lambda u, v: (fx + u * hpx * 1.15, fy - v * hpx), 'stand', (20, 20, 20), 3, fill=WHITE)

# ── 보조 모니터 (선택)
poly([(0, 1.0, 1.05), (0, 1.9, 1.05), (0, 1.9, 1.6), (0, 1.0, 1.6)], fill=(60, 60, 60), width_=2)
for k, ln in enumerate([0.25, 0.45, 0.65]):
    a3, b3 = P(0, 1.1, 1.5 - k * 0.13), P(0, 1.1 + ln, 1.5 - k * 0.13)
    d.line([a3, b3], fill=(190, 190, 190), width=3)

# ── 워크스테이션 (구역 밖)
X0, X1, Y0, Y1, Z1 = 3.35, 3.85, 0.05, 0.6, 0.95
poly([(X0, Y1, 0), (X1, Y1, 0), (X1, Y1, Z1), (X0, Y1, Z1)], fill=(230, 230, 230))
poly([(X1, Y0, 0), (X1, Y1, 0), (X1, Y1, Z1), (X1, Y0, Z1)], fill=(210, 210, 210))
poly([(X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1)], fill=(245, 245, 245))

# ── 치수
def dim(a, b, text, off, k=1.6):
    (x0, y0), (x1, y1) = P(*a), P(*b)
    ox, oy = off
    d.line([(x0 + ox, y0 + oy), (x1 + ox, y1 + oy)], fill=BLACK, width=1)
    for (xx, yy) in [(x0, y0), (x1, y1)]:
        d.line([(xx, yy), (xx + ox * 1.15, yy + oy * 1.15)], fill=LIGHT, width=1)
    T((x0 + x1) / 2 + ox * k, (y0 + y1) / 2 + oy * k - 12, text, 22, BLACK, 'center')

dim((0, ZD, 0), (ZW, ZD, 0), '3.2m', (-34, 60))
dim((ZW, 0, 0), (ZW, ZD, 0), '3.2m', (60, -34))
dim((0, ZD, 0), (0, ZD, WH), '2.6m (min 2.4m)', (-70, 0), k=3.0)
dashed((sx - 0.75, 0, 0), (sx - 0.75, sy, 0), color=BLACK, w=1, dash=8, gap=6)
dashed((sx - 0.75, sy, 0), (sx - 0.35, sy, 0), color=BLACK, w=1, dash=4, gap=4)
mx, my = P(sx - 0.75, sy, 0)
T(mx - 16, my - 4, '1.2m', 22, BLACK, 'right')

# ── 라벨 (영문 키워드 + 한글 한 줄)
leader((DX0 + 0.15, 0, DZ1 - 0.15), (1500, 250), 'SCREEN', '벽면 투사 2.7 × 2.0m (4:3)')
leader((cx, 0, DZ1 + 0.14), (1560, 390), 'CAMERA', '깊이 카메라 1대 · 보유')
leader((3.07, 0, 2.42), (1880, 520), 'SPEAKER ×2', '저음량 공간 사운드')
leader((PX1, PY0, PZ), (1820, 700), 'PROJECTOR', '초단초점 · 과학관 보유 · 보호 커버')
leader((X1, Y0, Z1), (1840, 900), 'WORKSTATION', '작가 구매 · 잠금 캐비닛')
leader((sx + 0.35, sy, 0), (1500, 1360), 'SPOT', '1인 1회 캡처 · 3~5초')
leader((0, 1.45, 1.6), (380, 700), 'MONITOR (Option)', '누적 기록 표시')
leader((0.5, 2.7, 0), (380, 1240), 'VIEW ZONE', '관람 · 대기 — 뒤 통행 없음')

# ── 각주
T(M, H - 70, 'Contactless · No Network · Low Light — 비접촉 체험, 현장 로컬 연산, 투사면 주변 조도 낮게', 20, MID)

img.convert('RGB').save('fig_iso_install.png')
print('saved fig_iso_install.png')
