"""「우리의 인상」 시스템 파이프라인 — 미니멀 버전 (흑백·그레이).

구성: 위 = 관람 단계 4개 / 가운데 = 9단계 / 아래 = HARDWARE · SOUND · CANVAS · LOG.
채운 검정 박스 = 이번 전시를 위해 제작, 회색 박스 = 보유 · 구현 완료.
실행: python3 fig_pipeline_ours.py → fig_pipeline_ours.png
"""
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def f(sz):
    return ImageFont.truetype(FONT, sz)

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
DARK  = (70, 70, 70)
MID   = (140, 140, 140)
LIGHT = (205, 205, 205)
PALE  = (236, 236, 236)

# (번호, 영문 키워드, 한글 요약, 제작 여부)
STEPS = [
    ('01', 'DETECT',  '감지',        False),
    ('02', 'CAPTURE', '1인 1회',     False),
    ('03', 'ANALYZE', '표정 분석',   True),
    ('04', 'MAP',     '4방향 변환',  False),
    ('05', 'JUDGE',   '24 슬롯',     False),
    ('06', 'MESSAGE', '비춤 + 질문', True),
    ('07', 'RENDER',  '영상 · 소리', True),
    ('08', 'BLEND',   '스며들기',    True),
    ('09', 'ARCHIVE', '익명 기록',   True),
]
PHASES = [(0, 1, 'FACE', '마주하기'), (2, 4, 'READ', '읽기'),
          (5, 6, 'REFLECT', '비추기'), (7, 8, 'LEAVE', '남기기')]

W, H = 2200, 900
img = Image.new('RGB', (W, H), WHITE)
d = ImageDraw.Draw(img)

def ctext(cx, y, text, font, fill):
    bb = d.textbbox((0, 0), text, font=font)
    d.text((cx - (bb[2] - bb[0]) // 2, y), text, font=font, fill=fill)

def head(x, y, direction, color=BLACK, s=8):
    pts = {'down': [(x - s, y - s - 4), (x + s, y - s - 4), (x, y)],
           'up':   [(x - s, y + s + 4), (x + s, y + s + 4), (x, y)],
           'left': [(x + s + 4, y - s), (x + s + 4, y + s), (x, y)]}[direction]
    d.polygon(pts, fill=color)

# ── 제목
M = 80
d.text((M, 60), 'PIPELINE', font=f(26), fill=MID)
d.text((M, 96), '「우리의 인상」 — 서서, 비추고, 남기다', font=f(44), fill=BLACK)
d.text((M, 160), '1인 1회 캡처 · 떠난 사람의 색이 쌓여 다음 사람의 화면이 된다', font=f(24), fill=DARK)

# ── 9단계
N, GAP = len(STEPS), 22
BW = (W - 2 * M - GAP * (N - 1)) // N
BY, BH = 330, 150
xs = [M + i * (BW + GAP) for i in range(N)]
BOT = BY + BH

# 관람 단계: 얇은 선 + 영문/한글
for a, b, en, ko in PHASES:
    x0, x1 = xs[a], xs[b] + BW
    d.line([(x0, 300), (x1, 300)], fill=BLACK, width=2)
    d.text((x0, 258), en, font=f(24), fill=BLACK)
    eb = d.textbbox((0, 0), en, font=f(24))
    d.text((x0 + (eb[2] - eb[0]) + 12, 262), ko, font=f(20), fill=MID)

for i, (num, en, ko, new) in enumerate(STEPS):
    x = xs[i]
    if new:
        d.rectangle([x, BY, x + BW, BOT], fill=BLACK)
        c1, c2, c3 = (150, 150, 150), WHITE, (190, 190, 190)
    else:
        d.rectangle([x, BY, x + BW, BOT], fill=PALE)
        c1, c2, c3 = MID, BLACK, DARK
    d.text((x + 14, BY + 12), num, font=f(20), fill=c1)
    ctext(x + BW // 2, BY + 54, en, f(30), c2)
    ctext(x + BW // 2, BY + 100, ko, f(21), c3)
    if i < N - 1:
        ay = BY + BH // 2
        d.line([(x + BW + 4, ay), (x + BW + GAP - 6, ay)], fill=LIGHT, width=2)

# ── 아래 한 줄: HARDWARE · SOUND · CANVAS · LOG
CY, CH = 560, 170

def block(x0, x1, title, rows):
    d.line([(x0, CY), (x1, CY)], fill=BLACK, width=2)
    d.text((x0, CY + 14), title, font=f(24), fill=BLACK)
    for k, r in enumerate(rows):
        y = CY + 58 + k * 34
        if isinstance(r, tuple):
            d.text((x0, y), r[0], font=f(20), fill=MID)
            d.text((x0 + 120, y), r[1], font=f(20), fill=DARK)
        else:
            d.text((x0, y), r, font=f(20), fill=DARK)

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

# 연결선: 07 → SOUND / 08 → CANVAS → 07 / 09 → LOG
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
d.text((c7 + 10, BOT + 22), 'loop', font=f(18), fill=MID)

c9 = xs[8] + BW // 2
d.line([(c9, BOT), (c9, CY - 14)], fill=BLACK, width=2)
head(c9, CY - 2, 'down')

# ── 범례 · 각주
LY = H - 110
d.rectangle([M, LY, M + 26, LY + 26], fill=BLACK)
d.text((M + 40, LY), 'New — 이번 전시 제작', font=f(22), fill=BLACK)
d.rectangle([M + 340, LY, M + 366, LY + 26], fill=PALE)
d.text((M + 380, LY), 'Ready — 보유 · 구현 완료', font=f(22), fill=BLACK)
d.text((M, H - 58), 'Privacy — 얼굴 영상은 저장하지 않고 즉시 파기, 익명 수치만 남긴다.', font=f(20), fill=MID)

img.save('fig_pipeline_ours.png')
print('saved fig_pipeline_ours.png')
