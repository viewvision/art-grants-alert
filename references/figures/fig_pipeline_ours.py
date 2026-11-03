"""「우리의 인상」 시스템 파이프라인 (국립중앙과학관 특별전 버전).

「감정의 인상」 9단계에서 달라진 점: 반응 재캡처 없음(1인 1회 캡처),
문구 = 비춰주기 + 건네는 질문, 축적 캔버스가 다음 관람객의 화면으로 되돌아옴.
실행: python3 fig_pipeline_ours.py → fig_pipeline_ours.png
"""
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def f(sz):
    return ImageFont.truetype(FONT, sz)

BG    = (250, 249, 246)
INK   = (28, 34, 48)
SUB   = (110, 118, 132)
FAINT = (168, 174, 184)
NAVY  = (36, 54, 92)      # 이번 제작
GRAY  = (196, 200, 208)   # 보유·완료
ACCENT = (214, 96, 60)
TEAL  = (40, 150, 160)

STEPS = [
    ('1', '감지',   '관람객 진입 · 거리',      '보유'),
    ('2', '캡처',   '1인 1회 · 3~5초 평균',    '보유'),
    ('3', '분석',   '얼굴 근육 단위 → 6감정',  '제작'),
    ('4', '변환',   '4방향 비율 · 밝기 · 강도', '완료'),
    ('5', '판정',   '24개 중 1개 슬롯',        '완료'),
    ('6', '문구',   '비춰주기 + 건네는 질문',  '제작'),
    ('7', '렌더',   '영상 + 소리 실시간 합성', '제작'),
    ('8', '스며들기', '퇴장 시 축적 화면에 더함', '제작'),
    ('9', '기록',   '익명 1행 · 화면 주기 저장', '제작'),
]

W, H = 2200, 1020
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

d.text((70, 50), '「우리의 인상」 시스템 파이프라인 — 한 사람이 서서 떠나기까지', font=f(46), fill=INK)
d.text((70, 118), '캡처는 한 사람당 한 번. 떠난 사람의 색이 화면에 쌓여, 다음 사람이 마주하는 화면이 된다.', font=f(26), fill=SUB)
d.line([(70, 166), (W - 70, 166)], fill=INK, width=3)

N = len(STEPS)
MARGIN, GAP = 70, 26
BOX_W = (W - MARGIN * 2 - GAP * (N - 1)) // N
BOX_H, BOX_Y = 190, 300
xs = [MARGIN + i * (BOX_W + GAP) for i in range(N)]

def center_text(x, w, y, text, font, fill):
    bb = d.textbbox((0, 0), text, font=font)
    d.text((x + (w - (bb[2] - bb[0])) // 2, y), text, font=font, fill=fill)

for i, (num, name, out, kind) in enumerate(STEPS):
    x = xs[i]
    dev = kind == '제작'
    fill = NAVY if dev else GRAY
    txt = (255, 255, 255) if dev else (52, 60, 74)
    sub = (196, 206, 226) if dev else (96, 104, 118)
    d.rounded_rectangle([x, BOX_Y, x + BOX_W, BOX_Y + BOX_H], radius=14, fill=fill)
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

# ── 3초 브래킷 (1~7)
b_x0, b_x1 = xs[0], xs[6] + BOX_W
b_y = BOX_Y - 40
d.line([(b_x0, b_y), (b_x1, b_y)], fill=ACCENT, width=3)
d.line([(b_x0, b_y), (b_x0, b_y + 14)], fill=ACCENT, width=3)
d.line([(b_x1, b_y), (b_x1, b_y + 14)], fill=ACCENT, width=3)
center_text(b_x0, b_x1 - b_x0, b_y - 44, '1~7단계 · 서면 3초 안에 색이 맺히기 시작', f(28), ACCENT)

# ── 축적 루프: 8 → 축적 화면 → 7 (다음 관람객)
cx7 = xs[6] + BOX_W // 2
cx8 = xs[7] + BOX_W // 2
ly = BOX_Y + BOX_H + 110
bt = ly + 22                       # 축적 화면 박스 윗변
d.line([(cx8, BOX_Y + BOX_H), (cx8, bt - 14)], fill=TEAL, width=4)
d.polygon([(cx8 - 11, bt - 18), (cx8 + 11, bt - 18), (cx8, bt - 2)], fill=TEAL)
d.line([(cx7, bt), (cx7, BOX_Y + BOX_H + 14)], fill=TEAL, width=4)
d.polygon([(cx7 - 11, BOX_Y + BOX_H + 18), (cx7 + 11, BOX_Y + BOX_H + 18), (cx7, BOX_Y + BOX_H + 2)], fill=TEAL)
d.text((cx8 + 16, BOX_Y + BOX_H + 98), '떠난 사람의 색', font=f(20), fill=TEAL)
d.text((cx7 - 16, BOX_Y + BOX_H + 98), '다음 사람에게', font=f(20), fill=TEAL, anchor='ra')
d.rounded_rectangle([cx7 - 150, bt, cx8 + 150, bt + 100], radius=12, outline=TEAL, width=3, fill=(232, 246, 247))
center_text(cx7 - 150, cx8 - cx7 + 300, bt + 12, '축적 화면 (110일 누적)', f(28), TEAL)
center_text(cx7 - 150, cx8 - cx7 + 300, bt + 54, '옵션: 일 단위 리셋 · 날짜별 스냅샷 보존', f(22), SUB)

# ── 9 → 누적 기록 (보조 모니터)
cx9 = xs[8] + BOX_W // 2
d.line([(cx9, BOX_Y + BOX_H), (cx9, ly + 160)], fill=SUB, width=3)
d.polygon([(cx9 - 10, ly + 152), (cx9 + 10, ly + 152), (cx9, ly + 168)], fill=SUB)
center_text(xs[8] - 60, BOX_W + 60, ly + 176, '누적 기록 → 보조 모니터', f(24), INK)

# ── 사운드 레인 (영상과 같은 값으로 움직임)
sy = ly + 30
SH = 150
lx0, lx1 = xs[0], xs[4] + BOX_W
d.rounded_rectangle([lx0, sy, lx1, sy + SH], radius=12, outline=ACCENT, width=3, fill=(252, 241, 236))
d.text((lx0 + 24, sy + 14), '공간 사운드 — 화면과 같은 값으로 함께 변한다', font=f(28), fill=INK)
rows = [
    '바탕층  축적 화면의 원소 비율 → 4원소 바탕음 믹스 (아무도 없을 때도 흐름)',
    '개인층  내 상위 두 원소 · 강도 → 소리 밀도·밝기 · 움직임 → 입자음·좌우 위치',
    '스며듦  떠날 때 내 소리가 잔향으로 풀려 바탕층에 섞임',
]
for k, r in enumerate(rows):
    d.text((lx0 + 24, sy + 58 + k * 30), r, font=f(21), fill=SUB)
# 7단계 → 사운드 레인 연결
c7 = xs[6] + 30
yb = BOX_Y + BOX_H
d.line([(c7, yb), (c7, yb + 78)], fill=ACCENT, width=3)
d.line([(c7, yb + 78), (lx1 - 70, yb + 78)], fill=ACCENT, width=3)
d.line([(lx1 - 70, yb + 78), (lx1 - 70, sy - 12)], fill=ACCENT, width=3)
d.polygon([(lx1 - 80, sy - 16), (lx1 - 60, sy - 16), (lx1 - 70, sy - 1)], fill=ACCENT)
d.text((lx1 - 50, yb + 88), '소리', font=f(20), fill=ACCENT)

# ── 범례
ly2 = H - 100
d.rounded_rectangle([MARGIN, ly2, MARGIN + 34, ly2 + 26], radius=6, fill=NAVY)
d.text((MARGIN + 48, ly2 - 2), '이번 전시를 위해 제작', font=f(26), fill=INK)
d.rounded_rectangle([MARGIN + 360, ly2, MARGIN + 394, ly2 + 26], radius=6, fill=GRAY)
d.text((MARGIN + 408, ly2 - 2), '보유 장비로 시험 완료 · 엔진 구현 완료', font=f(26), fill=INK)
d.text((MARGIN, H - 52),
       '※ 얼굴 영상은 장비 밖으로 나가지 않고 3단계 직후 파기된다. 모든 연산은 현장 워크스테이션에서 이루어지며 네트워크는 쓰지 않는다.',
       font=f(23), fill=FAINT)

img.save('fig_pipeline_ours.png')
print('saved fig_pipeline_ours.png')
