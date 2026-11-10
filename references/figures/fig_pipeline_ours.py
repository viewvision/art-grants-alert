"""「우리의 인상」 시스템 파이프라인 — 미니멀 버전 (흑백·그레이).

글꼴: 영문·숫자·기호 = Arial 계열(Liberation Sans, Arial과 글자 폭 동일) Bold,
      한글 = WenQuanYi Zen Hei (Arial에는 한글 글리프가 없음).
구성: 위 = 관람 단계 4개 / 가운데 = 9단계 / 아래 = HARDWARE · SOUND · CANVAS · LOG.
채운 검정 박스 = 이번 전시를 위해 제작, 회색 박스 = 보유 · 구현 완료.
실행: python3 fig_pipeline_ours.py → fig_pipeline_ours.png
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
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]

def is_korean(ch):
    o = ord(ch)
    return (0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F
            or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF)

def runs(text):
    """텍스트를 (문자열, 한글여부) 덩어리로 나눈다. 공백은 앞 덩어리에 붙인다."""
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
LIGHT = (205, 205, 205)
PALE  = (236, 236, 236)

W, H = 2200, 900
img = Image.new('RGB', (W, H), WHITE)
d = ImageDraw.Draw(img)

def width(text, size):
    return sum(d.textlength(t, font=font(KOREAN if k else LATIN_BOLD, size)) for t, k in runs(text))

def T(x, y, text, size, fill, align='left'):
    """y = 글자 윗선 기준. 한 기준선 위에 영문(Bold)과 한글을 이어서 그린다."""
    if align == 'center':
        x -= width(text, size) / 2
    base = y + size * 0.82
    for t, k in runs(text):
        fnt = font(KOREAN if k else LATIN_BOLD, size)
        d.text((x, base), t, font=fnt, fill=fill, anchor='ls')
        x += d.textlength(t, font=fnt)

def head(x, y, direction, color=BLACK, s=8):
    pts = {'down': [(x - s, y - s - 4), (x + s, y - s - 4), (x, y)],
           'up':   [(x - s, y + s + 4), (x + s, y + s + 4), (x, y)],
           'left': [(x + s + 4, y - s), (x + s + 4, y + s), (x, y)]}[direction]
    d.polygon(pts, fill=color)

# (영문 키워드, 한글 요약, 제작 여부)
STEPS = [
    ('DETECT',  '감지',        False),
    ('CAPTURE', '1인 1회',     False),
    ('ANALYZE', '표정 분석',   True),
    ('MAP',     '4방향 변환',  False),
    ('JUDGE',   '24 슬롯',     False),
    ('MESSAGE', '비춤 + 질문', True),
    ('RENDER',  '영상 · 소리', True),
    ('BLEND',   '스며들기',    True),
    ('ARCHIVE', '익명 기록',   True),
]
PHASES = [(0, 1, 'FACE', '마주하기'), (2, 4, 'READ', '읽기'),
          (5, 6, 'REFLECT', '비추기'), (7, 8, 'LEAVE', '남기기')]

# ── 제목
M = 80
T(M, 60, 'PIPELINE', 24, MID)
T(M, 98, '「우리의 인상」 — 서서, 비추고, 남기다', 44, BLACK)
T(M, 164, '1인 1회 캡처 · 떠난 사람의 색이 쌓여 다음 사람의 화면이 된다', 24, DARK)

# ── 9단계
N, GAP = len(STEPS), 22
BW = (W - 2 * M - GAP * (N - 1)) // N
BY, BH = 330, 140
xs = [M + i * (BW + GAP) for i in range(N)]
BOT = BY + BH

for a, b, en, ko in PHASES:
    x0, x1 = xs[a], xs[b] + BW
    d.line([(x0, 300), (x1, 300)], fill=BLACK, width=2)
    T(x0, 262, en, 24, BLACK)
    T(x0 + width(en, 24) + 12, 265, ko, 20, MID)

for i, (en, ko, new) in enumerate(STEPS):
    x = xs[i]
    if new:
        d.rectangle([x, BY, x + BW, BOT], fill=BLACK)
        c_en, c_ko = WHITE, (190, 190, 190)
    else:
        d.rectangle([x, BY, x + BW, BOT], fill=PALE)
        c_en, c_ko = BLACK, DARK
    T(x + BW / 2, BY + 38, en, 28, c_en, 'center')
    T(x + BW / 2, BY + 84, ko, 21, c_ko, 'center')
    if i < N - 1:
        ay = BY + BH // 2
        d.line([(x + BW + 4, ay), (x + BW + GAP - 6, ay)], fill=LIGHT, width=2)

# ── 아래 한 줄: HARDWARE · SOUND · CANVAS · LOG
CY = 560

def block(x0, x1, title, rows):
    d.line([(x0, CY), (x1, CY)], fill=BLACK, width=2)
    T(x0, CY + 16, title, 24, BLACK)
    for k, r in enumerate(rows):
        y = CY + 60 + k * 34
        if isinstance(r, tuple):
            T(x0, y, r[0], 20, MID)
            T(x0 + 130, y, r[1], 20, DARK)
        else:
            T(x0, y, r, 20, DARK)

block(xs[0], xs[2] + BW, 'HARDWARE',
      [('Input', '깊이 카메라 1대'),
       ('Compute', '워크스테이션 · Local, No Network'),
       ('Output', '프로젝터 · 스피커 2조')])
block(xs[3], xs[5] + BW, 'SOUND  화면과 같은 값으로',
      [('Base', '축적 화면의 원소 비율'),
       ('Personal', '두 원소 · 강도 · 움직임'),
       ('Fade', '떠날 때 바탕음에 섞임')])
cx0 = xs[6] + 70
block(cx0, xs[7] + BW, 'CANVAS  110 days',
      ['Accumulated', '→ 다음 사람의 화면', 'Option: Daily Reset'])
block(xs[8], xs[8] + BW, 'LOG',
      ['Anonymous', '→ 보조 모니터'])

# 연결선: RENDER → SOUND / BLEND → CANVAS → RENDER / ARCHIVE → LOG
s7 = xs[6] + 30
my = CY + 80
d.line([(s7, BOT), (s7, my)], fill=MID, width=2)
d.line([(s7, my), (xs[5] + BW + 16, my)], fill=MID, width=2)
head(xs[5] + BW + 4, my, 'left', MID)

c8 = xs[7] + BW // 2
d.line([(c8, BOT), (c8, CY - 14)], fill=BLACK, width=2)
head(c8, CY - 2, 'down')
c7 = xs[6] + BW - 36
d.line([(c7, CY), (c7, BOT + 14)], fill=BLACK, width=2)
head(c7, BOT + 2, 'up')
T(c7 + 10, BOT + 24, 'loop', 18, MID)

c9 = xs[8] + BW // 2
d.line([(c9, BOT), (c9, CY - 14)], fill=BLACK, width=2)
head(c9, CY - 2, 'down')

# ── 범례 · 각주
LY = H - 110
d.rectangle([M, LY, M + 26, LY + 26], fill=BLACK)
T(M + 40, LY + 1, 'New — 이번 전시 제작', 22, BLACK)
d.rectangle([M + 340, LY, M + 366, LY + 26], fill=PALE)
T(M + 380, LY + 1, 'Ready — 보유 · 구현 완료', 22, BLACK)
T(M, H - 58, 'Privacy — 얼굴 영상은 저장하지 않고 즉시 파기, 익명 수치만 남긴다.', 20, MID)

img.save('fig_pipeline_ours.png')
print('saved fig_pipeline_ours.png')
