"""「우리의 인상」 설치 아이소메트릭 (국립중앙과학관 특별전 지원용).

단위는 미터. x = 벽을 따라(폭), y = 벽에서 관람객 쪽(깊이), z = 높이.
실행: python3 fig_iso_install.py → fig_iso_install.png
"""
import math
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def f(sz):
    return ImageFont.truetype(FONT, sz)

BG    = (250, 249, 246)
INK   = (28, 34, 48)
SUB   = (110, 118, 132)
FAINT = (170, 176, 186)
DIM   = (205, 208, 214)
FLOOR = (196, 198, 204)
WALL_B = (88, 92, 102)
WALL_L = (72, 76, 86)
ACCENT = (232, 106, 72)

# ── 공간 치수 (m)
ZW, ZD, WH = 3.2, 3.2, 2.6          # 구역 폭·깊이, 벽 높이
DX0, DX1 = 0.265, 2.935             # 투사 화면 폭 약 2.67m (4:3)
DZ0, DZ1 = 0.40, 2.40               # 투사 화면 높이 2.0m
STAND = (1.6, 1.2)                  # 체험 위치 (화면에서 1.2m)

W, H = 2200, 1760
S = 210                              # 1m = 210px
OX, OY = 1040, 800                   # 원점(벽 왼쪽 아래 모서리) 화면 좌표
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))

def P(x, y, z=0.0):
    return (OX + (x - y) * C30 * S, OY + (x + y) * S30 * S - z * S)

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img, 'RGBA')

def poly(pts, fill=None, outline=INK, width=2):
    q = [P(*p) for p in pts]
    if fill:
        d.polygon(q, fill=fill)
    if outline:
        d.line(q + [q[0]], fill=outline, width=width)

def dashed(a, b, color=SUB, width=2, dash=14, gap=10):
    (x0, y0), (x1, y1) = P(*a), P(*b)
    L = math.hypot(x1 - x0, y1 - y0)
    n = int(L // (dash + gap)) + 1
    for i in range(n):
        t0 = i * (dash + gap) / L
        t1 = min((i * (dash + gap) + dash) / L, 1)
        if t0 >= 1:
            break
        d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=color, width=width)

def label(xy, text, size=26, color=INK, anchor='la'):
    d.text(xy, text, font=f(size), fill=color, anchor=anchor)

def leader(pt3, txt_xy, lines, size=26):
    px, py = P(*pt3)
    d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=ACCENT)
    d.line([(px, py), txt_xy], fill=ACCENT, width=2)
    tx, ty = txt_xy
    for i, ln in enumerate(lines):
        label((tx + (8 if tx >= px else -8), ty - 14 + i * (size + 8)), ln,
              size=size if i == 0 else size - 4,
              color=INK if i == 0 else SUB,
              anchor='la' if tx >= px else 'ra')

# ── 헤더
label((70, 54), '「우리의 인상」 설치 아이소메트릭 (안)', 50)
label((70, 122), '국립중앙과학관 특별전 · 인터랙티브 아트 · 바닥 약 3.2m × 3.2m (10㎡ 이내) · 벽면 프로젝션 · 장비 규격은 협의 전 예시값', 26, SUB)
d.line([(70, 172), (W - 70, 172)], fill=INK, width=3)

# ── 바닥
poly([(0, 0, 0), (ZW, 0, 0), (ZW, ZD, 0), (0, ZD, 0)], fill=FLOOR, width=2)
# 관람·대기 영역 (체험 위치 뒤)
poly([(0, 2.0, 0), (ZW, 2.0, 0), (ZW, ZD, 0), (0, ZD, 0)],
     fill=(120, 150, 200, 40), outline=None)
for k in range(1, 12):
    t = k / 12
    dashed((t * ZW, 2.0, 0), (t * ZW, ZD, 0), color=(150, 170, 205), width=1, dash=6, gap=8)
dashed((0, 2.0, 0), (ZW, 2.0, 0), color=(110, 140, 190), width=2)

# ── 벽 (뒤·왼쪽)
poly([(0, 0, 0), (ZW, 0, 0), (ZW, 0, WH), (0, 0, WH)], fill=WALL_B)
poly([(0, 0, 0), (0, ZD, 0), (0, ZD, WH), (0, 0, WH)], fill=WALL_L)

# ── 투사 화면 (벽면 프로젝션 — 축적된 인상들이 겹친 화면)
cx = (DX0 + DX1) / 2
d.polygon([P(DX0, 0, DZ0), P(DX1, 0, DZ0), P(DX1, 0, DZ1), P(DX0, 0, DZ1)], fill=(214, 232, 242))
def silhouette(xc, zb, hgt, col, alpha):
    w = hgt * 0.24
    q = [P(xc - w * 0.55, 0, zb), P(xc + w * 0.55, 0, zb),
         P(xc + w, 0, zb + hgt * 0.62), P(xc + w * 0.8, 0, zb + hgt * 0.80),
         P(xc - w * 0.8, 0, zb + hgt * 0.80), P(xc - w, 0, zb + hgt * 0.62)]
    d.polygon(q, fill=col + (alpha,))
    hx, hy = P(xc, 0, zb + hgt * 0.90)
    r = hgt * 0.095 * S
    d.ellipse([hx - r, hy - r * 1.15, hx + r, hy + r * 1.15], fill=col + (alpha,))
# 앞선 관람객들의 인상 (겹겹이 스민 실루엣)
past = [(0.55, (120, 205, 235), 1.55), (0.95, (247, 180, 156), 1.45), (1.30, (194, 169, 240), 1.6),
        (1.95, (238, 208, 156), 1.5), (2.30, (73, 210, 227), 1.4), (2.62, (248, 130, 90), 1.55),
        (0.80, (232, 178, 88), 1.35), (2.10, (154, 114, 235), 1.5)]
for xc, col, hg in past:
    silhouette(xc, DZ0 + 0.05, hg, col, 95)
# 지금 선 관람객의 인상 (중앙, 더 선명)
silhouette(cx, DZ0 + 0.05, 1.7, (246, 82, 27), 150)
silhouette(cx, DZ0 + 0.05, 1.62, (0, 192, 216), 70)
poly([(DX0, 0, DZ0), (DX1, 0, DZ0), (DX1, 0, DZ1), (DX0, 0, DZ1)], fill=None, outline=(255, 255, 255), width=2)

# ── 초단초점 프로젝터 (벽 하단 바닥, 보호 커버)
PX0, PX1, PY0, PY1, PZ = cx - 0.25, cx + 0.25, 0.06, 0.36, 0.12
poly([(PX0, PY1, 0), (PX1, PY1, 0), (PX1, PY1, PZ), (PX0, PY1, PZ)], fill=(52, 56, 66))
poly([(PX1, PY0, 0), (PX1, PY1, 0), (PX1, PY1, PZ), (PX1, PY0, PZ)], fill=(40, 44, 54))
poly([(PX0, PY0, PZ), (PX1, PY0, PZ), (PX1, PY1, PZ), (PX0, PY1, PZ)], fill=(70, 74, 86))
for tx in [DX0, DX1]:
    dashed((cx, PY0 + 0.05, PZ), (tx, 0, DZ1), color=(255, 240, 200, 150), width=2, dash=10, gap=8)

# ── 앰비언스 스피커 2조 (투사 화면 좌우 상단)
for sxp in [0.13, 3.07]:
    poly([(sxp - 0.08, 0, 2.08), (sxp + 0.08, 0, 2.08), (sxp + 0.08, 0, 2.42), (sxp - 0.08, 0, 2.42)],
         fill=(30, 32, 40), outline=(150, 154, 164), width=2)
    hx, hy = P(sxp, 0, 2.2)
    d.ellipse([hx - 9, hy - 9, hx + 9, hy + 9], outline=(150, 154, 164), width=2)

# ── 깊이 센싱 카메라 (투사 화면 상단 중앙)
cam = [(cx - 0.13, 0, DZ1 + 0.04), (cx + 0.13, 0, DZ1 + 0.04),
       (cx + 0.13, 0, DZ1 + 0.14), (cx - 0.13, 0, DZ1 + 0.14)]
poly(cam, fill=(20, 22, 28), outline=(150, 154, 164), width=2)
sx, sy = STAND
for tgt in [(sx - 0.9, sy + 0.5, 0), (sx + 0.9, sy + 0.5, 0)]:
    dashed((cx, 0.02, DZ1 + 0.04), tgt, color=(232, 106, 72, 170), width=2)

# ── 체험 위치 바닥 표시
ring = [P(sx + 0.35 * math.cos(t), sy + 0.35 * math.sin(t), 0)
        for t in [i * 2 * math.pi / 48 for i in range(48)]]
d.polygon(ring, fill=(232, 106, 72, 60))
d.line(ring + [ring[0]], fill=ACCENT, width=3)

# ── 관람객 (1.65m)
fx, fy = P(sx, sy, 0)
hgt = 1.65 * S
body = [(fx - 21, fy), (fx + 21, fy), (fx + 27, fy - hgt * 0.55),
        (fx + 32, fy - hgt * 0.80), (fx - 32, fy - hgt * 0.80), (fx - 27, fy - hgt * 0.55)]
d.polygon(body, fill=(60, 66, 80))
d.ellipse([fx - 21, fy - hgt - 3, fx + 21, fy - hgt * 0.82], fill=(60, 66, 80))

# ── 보조 모니터 (선택, 왼쪽 벽)
poly([(0, 1.0, 1.05), (0, 1.9, 1.05), (0, 1.9, 1.6), (0, 1.0, 1.6)], fill=(46, 52, 64), width=3)
for k, ln in enumerate([0.25, 0.45, 0.65]):
    a3, b3 = P(0, 1.1, 1.5 - k * 0.13), P(0, 1.1 + ln, 1.5 - k * 0.13)
    d.line([a3, b3], fill=(255, 205, 120), width=4)

# ── 워크스테이션 (구역 밖 오른쪽 · 잠금 캐비닛)
X0, X1, Y0, Y1, Z1 = 3.35, 3.85, 0.05, 0.6, 0.95
poly([(X0, Y1, 0), (X1, Y1, 0), (X1, Y1, Z1), (X0, Y1, Z1)], fill=(200, 202, 208))
poly([(X1, Y0, 0), (X1, Y1, 0), (X1, Y1, Z1), (X1, Y0, Z1)], fill=(180, 183, 190))
poly([(X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1)], fill=(222, 224, 228))

# ── 치수선
def dim(a, b, text, off, size=26, k=1.6):
    (x0, y0), (x1, y1) = P(*a), P(*b)
    ox, oy = off
    d.line([(x0 + ox, y0 + oy), (x1 + ox, y1 + oy)], fill=INK, width=2)
    for (xx, yy) in [(x0, y0), (x1, y1)]:
        d.line([(xx, yy), (xx + ox * 1.15, yy + oy * 1.15)], fill=FAINT, width=1)
    label(((x0 + x1) / 2 + ox * k, (y0 + y1) / 2 + oy * k), text, size, INK, 'mm')

dim((0, ZD, 0), (ZW, ZD, 0), '3.2m', (-34, 60))
dim((ZW, 0, 0), (ZW, ZD, 0), '3.2m', (60, -34))
dim((0, ZD, 0), (0, ZD, WH), '2.6m (최소 2.4m)', (-70, 0), k=3.0)
# 화면 ↔ 체험 위치 거리
dashed((sx - 0.75, 0, 0), (sx - 0.75, sy, 0), color=INK, width=2, dash=8, gap=6)
dashed((sx - 0.75, sy, 0), (sx - 0.35, sy, 0), color=INK, width=1, dash=4, gap=4)
mx, my = P(sx - 0.75, 0.6, 0)
label((mx - 14, my), '화면에서 약 1.2m', 24, INK, 'rm')

# ── 지시선 라벨
leader((DX0 + 0.15, 0, DZ1 - 0.15), (1500, 250),
       ['벽면 투사 화면', '약 2.7m × 2.0m (4:3) · 축적된 인상이 겹친 화면'])
leader((PX1, PY0, PZ), (1820, 700),
       ['초단초점 프로젝터 1대', '과학관 보유 장비 · 바닥 보호 커버'])
leader((3.07, 0, 2.42), (1880, 520),
       ['앰비언스 스피커 2조', '+ 소형 앰프 · 저음량 공간음'])
leader((cx, 0, DZ1 + 0.14), (1560, 400),
       ['깊이 센싱 카메라 1대 (작가 보유)', '실루엣·표정·자세를 한 대로 동시 인식'])
leader((0, 1.45, 1.6), (380, 700),
       ['보조 모니터 (선택)', '누적 기록 상시 표시'])
leader((sx + 0.35, sy, 0), (1500, 1390),
       ['체험 위치 바닥 표시', '여기 서면 1회 캡처 (3~5초)'])
leader((X1, Y0, Z1), (1840, 900),
       ['워크스테이션', '작가 구매·반입', '잠금 캐비닛 · 무인 자동 실행'])
leader((0.5, 2.7, 0), (380, 1260),
       ['관람·대기 영역', '체험 위치 뒤를 가로지르는', '통행 동선은 두지 않음'])

# ── 하단 메모
d.line([(70, H - 170), (W - 70, H - 170)], fill=DIM, width=2)
notes = [
    '· 비접촉 체험 — 터치·조작 장치 없음. 프로젝터는 보호 커버로 덮고, 바닥 케이블은 몰딩 처리.',
    '· 네트워크 불필요 — 인식·문구·렌더 모두 현장 장비에서 연산. 얼굴 원본은 저장하지 않음.',
    '· 조명 — 투사면 주변 조도를 낮게 유지하고, 카메라 정면 직사광·적외선 조명을 피함. 장비 규격은 과학관 협의 후 확정.',
]
for i, n in enumerate(notes):
    label((70, H - 145 + i * 40), n, 25, SUB)

img.save('fig_iso_install.png')
print('saved fig_iso_install.png')
