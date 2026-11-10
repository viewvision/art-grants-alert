"""「우리의 인상」 시스템 파이프라인 (국립중앙과학관 특별전 버전).

「감정의 인상」 9단계에서 달라진 점: 반응 재캡처 없음(1인 1회 캡처),
문구 = 비춰주기 + 건네는 질문, 축적 캔버스가 다음 관람객의 화면으로 되돌아옴,
소리가 화면과 같은 값으로 함께 변함.
구성: 위 = 관람 단계 묶음 / 가운데 = 9단계 / 아래 = 장비 · 소리 · 축적 화면 · 기록.
실행: python3 fig_pipeline_ours.py → fig_pipeline_ours.png
"""
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def f(sz):
    return ImageFont.truetype(FONT, sz)

BG     = (250, 249, 246)
INK    = (28, 34, 48)
SUB    = (110, 118, 132)
FAINT  = (168, 174, 184)
NAVY   = (36, 54, 92)      # 이번 전시를 위해 제작
GRAY   = (196, 200, 208)   # 보유 · 완료
ACCENT = (214, 96, 60)     # 소리
TEAL   = (40, 150, 160)    # 축적 화면

STEPS = [
    ('1', '감지',     '관람객 진입 · 거리',        '보유'),
    ('2', '캡처',     '1인 1회 · 3~5초 평균',      '보유'),
    ('3', '분석',     '얼굴 근육 단위 → 6감정',    '제작'),
    ('4', '변환',     '4방향 비율 · 밝기 · 강도',  '완료'),
    ('5', '판정',     '24개 중 1개 슬롯',          '완료'),
    ('6', '문구',     '비춰주기 + 건네는 질문',    '제작'),
    ('7', '렌더',     '영상 + 소리 실시간 합성',   '제작'),
    ('8', '스며들기', '퇴장 시 축적 화면에 더함',  '제작'),
    ('9', '기록',     '익명 1행 · 화면 주기 저장', '제작'),
]

# 관람 단계 묶음: (시작 인덱스, 끝 인덱스, 이름, 설명, 색)
PHASES = [
    (0, 1, '마주하기', '서면 바로 시작',         (226, 229, 236)),
    (2, 4, '읽기',     '얼굴 → 감정 → 슬롯',     (222, 228, 240)),
    (5, 6, '비추기',   '색이 맺히는 3~5초',      (244, 228, 220)),
    (7, 8, '남기기',   '떠날 때',                (218, 238, 240)),
]

W, H = 2200, 1000
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

def center_text(x, w, y, text, font, fill):
    bb = d.textbbox((0, 0), text, font=font)
    d.text((x + (w - (bb[2] - bb[0])) // 2, y), text, font=font, fill=fill)

def arrow_head(x, y, direction, color, s=10):
    if direction == 'down':
        d.polygon([(x - s, y - s - 4), (x + s, y - s - 4), (x, y)], fill=color)
    elif direction == 'up':
        d.polygon([(x - s, y + s + 4), (x + s, y + s + 4), (x, y)], fill=color)
    elif direction == 'left':
        d.polygon([(x + s + 4, y - s), (x + s + 4, y + s), (x, y)], fill=color)

# ── 제목
d.text((70, 50), '「우리의 인상」 시스템 파이프라인 — 한 사람이 서서 떠나기까지', font=f(46), fill=INK)
d.text((70, 118), '캡처는 한 사람당 한 번. 서면 3초 안에 색이 맺히기 시작하고, 떠날 때 그 색이 화면에 쌓여 다음 사람이 마주하는 화면이 된다.',
       font=f(25), fill=SUB)
d.line([(70, 166), (W - 70, 166)], fill=INK, width=3)

# ── 9단계 박스 좌표
N = len(STEPS)
MARGIN, GAP = 70, 26
BOX_W = (W - MARGIN * 2 - GAP * (N - 1)) // N
BOX_Y, BOX_H = 300, 190
xs = [MARGIN + i * (BOX_W + GAP) for i in range(N)]
BOT = BOX_Y + BOX_H

# ── 관람 단계 묶음 (박스 위)
PY, PH = 214, 62
for a, b, name, desc, col in PHASES:
    x0, x1 = xs[a], xs[b] + BOX_W
    d.rounded_rectangle([x0, PY, x1, PY + PH], radius=12, fill=col)
    d.text((x0 + 20, PY + 14), name, font=f(28), fill=INK)
    nb = d.textbbox((0, 0), name, font=f(28))
    d.text((x0 + 20 + (nb[2] - nb[0]) + 16, PY + 21), desc, font=f(21), fill=SUB)

# ── 9단계 박스
for i, (num, name, out, kind) in enumerate(STEPS):
    x = xs[i]
    dev = kind == '제작'
    fill = NAVY if dev else GRAY
    txt = (255, 255, 255) if dev else (52, 60, 74)
    sub = (196, 206, 226) if dev else (96, 104, 118)
    d.rounded_rectangle([x, BOX_Y, x + BOX_W, BOT], radius=14, fill=fill)
    d.text((x + 16, BOX_Y + 14), num, font=f(26), fill=sub)
    center_text(x, BOX_W, BOX_Y + 60, name, f(36), txt)
    words = out.split(' ')
    lines = [out]
    if d.textbbox((0, 0), out, font=f(22))[2] > BOX_W - 20:
        mid = (len(words) + 1) // 2
        lines = [' '.join(words[:mid]), ' '.join(words[mid:])]
    for k, ln in enumerate(lines):
        center_text(x, BOX_W, BOX_Y + 118 + k * 30, ln, f(22), sub)
    if i < N - 1:
        ax, ay = x + BOX_W + 4, BOX_Y + BOX_H // 2
        d.polygon([(ax, ay - 9), (ax + GAP - 8, ay), (ax, ay + 9)], fill=(190, 194, 202))

# ── 아래 카드 한 줄
CY, CH = 610, 190

def card(x0, x1, outline, fill, title, title_col, rows, row_size=20):
    d.rounded_rectangle([x0, CY, x1, CY + CH], radius=12, outline=outline, width=3, fill=fill)
    d.text((x0 + 22, CY + 16), title, font=f(27), fill=title_col)
    for k, r in enumerate(rows):
        d.text((x0 + 22, CY + 64 + k * 36), r, font=f(row_size), fill=SUB)

# (1) 장비 — 1~3단계 아래
card(xs[0], xs[2] + BOX_W, (150, 156, 168), (244, 245, 248),
     '장비 — 세 덩어리', INK,
     ['입력   깊이 센싱 카메라 1대 (보유)',
      '연산   워크스테이션 1대 · 현장 로컬, 네트워크 없음',
      '출력   초단초점 프로젝터 1대 · 스피커 2조'])
for i in (0, 1, 2):
    cx = xs[i] + BOX_W // 2
    for y in range(BOT + 8, CY - 6, 14):
        d.line([(cx, y), (cx, min(y + 7, CY - 6))], fill=(170, 176, 186), width=2)

# (2) 소리 — 4~6단계 아래, 7단계에서 들어옴
sx0, sx1 = xs[3], xs[5] + BOX_W
card(sx0, sx1, ACCENT, (252, 241, 236),
     '소리 — 화면과 같은 값으로 함께 변한다', INK,
     ['바탕층   축적 화면의 원소 비율 → 4원소 바탕음',
      '개인층   두 원소·강도·밝기 → 밀도·배음 / 움직임 → 입자음·좌우',
      '스며듦   떠날 때 잔향으로 풀려 바탕층에 섞임'])
lx = xs[6] + 34
ly = CY + CH // 2
d.line([(lx, BOT), (lx, ly)], fill=ACCENT, width=4)
d.line([(lx, ly), (sx1 + 18, ly)], fill=ACCENT, width=4)
arrow_head(sx1 + 4, ly, 'left', ACCENT)
d.text((lx - 10, BOT + 40), '소리', font=f(20), fill=ACCENT, anchor='ra')

# (3) 축적 화면 — 7~8단계 아래, 8 → 카드 → 7 순환
ax0, ax1 = xs[6] + 70, xs[7] + BOX_W
card(ax0, ax1, TEAL, (232, 246, 247),
     '축적 화면 (110일 누적)', TEAL,
     ['다음 관람객이 마주하는 화면',
      '옵션: 일 단위 리셋',
      '날짜별 스냅샷 보존'])
c8 = xs[7] + BOX_W // 2
d.line([(c8, BOT), (c8, CY - 16)], fill=TEAL, width=4)
arrow_head(c8, CY - 2, 'down', TEAL)
d.text((c8 + 14, BOT + 40), '떠난 사람의 색', font=f(20), fill=TEAL)
c7 = xs[6] + BOX_W - 40
d.line([(c7, CY), (c7, BOT + 16)], fill=TEAL, width=4)
arrow_head(c7, BOT + 2, 'up', TEAL)
d.text((c7 + 12, BOT + 70), '다음 사람에게', font=f(20), fill=TEAL)

# (4) 기록 — 9단계 아래
card(xs[8], xs[8] + BOX_W, (150, 156, 168), (244, 245, 248),
     '누적 기록', INK,
     ['익명 수치만 저장', '보조 모니터에', '관찰 기록으로 표시'])
c9 = xs[8] + BOX_W // 2
d.line([(c9, BOT), (c9, CY - 16)], fill=SUB, width=3)
arrow_head(c9, CY - 2, 'down', SUB)

# ── 범례 · 각주
LY = H - 120
d.rounded_rectangle([MARGIN, LY, MARGIN + 34, LY + 26], radius=6, fill=NAVY)
d.text((MARGIN + 48, LY - 2), '이번 전시를 위해 제작', font=f(25), fill=INK)
d.rounded_rectangle([MARGIN + 350, LY, MARGIN + 384, LY + 26], radius=6, fill=GRAY)
d.text((MARGIN + 398, LY - 2), '보유 장비로 시험 완료 · 엔진 구현 완료', font=f(25), fill=INK)
d.text((MARGIN, H - 64),
       '※ 얼굴 영상은 장비 밖으로 나가지 않고 3단계 직후 파기된다. 모든 연산은 현장 워크스테이션에서 이루어지며 네트워크는 쓰지 않는다.',
       font=f(23), fill=FAINT)

img.save('fig_pipeline_ours.png')
print('saved fig_pipeline_ours.png')
