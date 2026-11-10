"""감정 4방향 색채 체계 — 미니멀 버전 (흰 바탕 · 흑백 타이포, 색 견본만 컬러).

글꼴: 영문·숫자·기호 = Arial 계열(Liberation Sans, Arial과 글자 폭 동일) Bold,
      한글 = WenQuanYi Zen Hei (Arial에는 한글 글리프가 없음).
실행: python3 fig1_palette.py → fig_palette_4direction.png
"""
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
LIGHT = (215, 215, 215)

# (영문, 한글, 방향 키워드, 방향 설명, 색 3단계, 운동 키워드, 운동 설명)
ELEMENTS = [
    ('WATER', '물',   'Inward',  '안으로 가라앉음', ['96E2EC', '49D2E3', '00C0D8'], 'Sink',   '가라앉으며 고인다'),
    ('FIRE',  '불',   'Outward', '밖으로 터져 나옴', ['F7B49C', 'F8825A', 'F6521B'], 'Rise',   '피어오르며 번진다'),
    ('AIR',   '공기', 'Forward', '앞으로 향함',     ['C2A9F0', '9A72EB', '753EE4'], 'Drift',  '경계 없이 흩어진다'),
    ('EARTH', '흙',   'Here',    '지금 여기에 머묾', ['EED09C', 'E7B258', 'DC9418'], 'Gather', '구조를 이루며 응집한다'),
]
LEVELS = [('LOW', '저'), ('MID', '중'), ('HIGH', '고')]

W, H = 2200, 1260
img = Image.new('RGB', (W, H), WHITE)
d = ImageDraw.Draw(img)

def width(text, size):
    return sum(d.textlength(t, font=font(KOREAN if k else LATIN_BOLD, size)) for t, k in runs(text))

def T(x, y, text, size, fill, align='left'):
    if align == 'center':
        x -= width(text, size) / 2
    base = y + size * 0.82
    for t, k in runs(text):
        fnt = font(KOREAN if k else LATIN_BOLD, size)
        d.text((x, base), t, font=fnt, fill=fill, anchor='ls')
        x += d.textlength(t, font=fnt)

# ── 제목
M = 80
T(M, 58, 'COLOR SYSTEM', 24, MID)
T(M, 96, '감정의 방향이 곧 색이 된다', 44, BLACK)
T(M, 162, 'Arousal → 채도 · 속도   /   Valence → 번지는 방향   /   한 화면에는 상위 두 방향만', 22, DARK)

# ── 열 위치
X_EL   = M            # 원소
X_SW   = 560          # 견본 시작
SW_W, SW_GAP = 250, 24
X_MO   = X_SW + 3 * SW_W + 2 * SW_GAP + 90   # 운동

TOP = 280
T(X_EL, TOP, 'ELEMENT', 20, MID)
for i, (en, ko) in enumerate(LEVELS):
    T(X_SW + i * (SW_W + SW_GAP), TOP, f'{en} 강도 {ko}', 20, MID)
T(X_MO, TOP, 'MOTION', 20, MID)

ROW_Y, ROW_H = TOP + 50, 200
for r, (en, ko, dir_en, dir_ko, cols, mo_en, mo_ko) in enumerate(ELEMENTS):
    y = ROW_Y + r * ROW_H
    d.line([(M, y), (W - M, y)], fill=BLACK if r == 0 else LIGHT, width=2 if r == 0 else 1)
    T(X_EL, y + 34, en, 38, BLACK)
    T(X_EL + width(en, 38) + 16, y + 44, ko, 26, DARK)
    T(X_EL, y + 98, dir_en, 22, BLACK)
    T(X_EL + width(dir_en, 22) + 12, y + 99, dir_ko, 20, MID)
    for i, hexv in enumerate(cols):
        x = X_SW + i * (SW_W + SW_GAP)
        d.rectangle([x, y + 30, x + SW_W, y + 130], fill=tuple(bytes.fromhex(hexv)))
        T(x, y + 144, '#' + hexv, 18, MID)
    T(X_MO, y + 44, mo_en, 30, BLACK)
    T(X_MO, y + 92, mo_ko, 22, DARK)
d.line([(M, ROW_Y + 4 * ROW_H), (W - M, ROW_Y + 4 * ROW_H)], fill=BLACK, width=2)

# ── 각주
T(M, H - 70, 'Reference — 기준색이며, 실제 화면에서는 강도와 밝기 판정에 따라 연속적으로 변한다.', 20, MID)

img.save('fig_palette_4direction.png')
print('saved fig_palette_4direction.png')
