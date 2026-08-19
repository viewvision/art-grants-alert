from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def f(sz):
    return ImageFont.truetype(FONT, sz)

BG    = (250, 249, 246)
INK   = (28, 34, 48)
SUB   = (110, 118, 132)
FAINT = (168, 174, 184)

NAVY  = (36, 54, 92)      # 개발 단계
GRAY  = (196, 200, 208)   # 보유 기술 단계
ACCENT= (214, 96, 60)

# (번호, 이름, 산출물 요약, 보유/개발)
STEPS = [
    ('1', '감지',   '관객 유무 · 거리',  '보유'),
    ('2', '캡처',   'RGB 4K 프레임',     '보유'),
    ('3', '분석',   '6개 감정값',        '개발'),
    ('4', '변환',   '4방향 비율 · 톤 · 강도', '개발'),
    ('5', '판정',   '24개 중 1개 슬롯',  '개발'),
    ('6', '문구 생성', '표시 문구 1문장',  '개발'),
    ('7', '렌더',   '실시간 화면',       '보유'),
    ('8', '반응 재캡처', '갱신 파라미터',  '개발'),
    ('9', '저장 · 퇴장', '익명 수치 로그',  '개발'),
]

W, H = 2200, 720
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

d.text((70, 50), '전체 시스템 파이프라인 — 캡처부터 표시까지 9단계', font=f(48), fill=INK)
d.line([(70, 128), (W - 70, 128)], fill=INK, width=3)

# ── 박스 배치
N = len(STEPS)
MARGIN = 70
GAP = 26
BOX_W = (W - MARGIN * 2 - GAP * (N - 1)) // N
BOX_H = 190
BOX_Y = 258

for i, (num, name, out, kind) in enumerate(STEPS):
    x = MARGIN + i * (BOX_W + GAP)
    fill = NAVY if kind == '개발' else GRAY
    txt  = (255, 255, 255) if kind == '개발' else (52, 60, 74)
    sub  = (196, 206, 226) if kind == '개발' else (96, 104, 118)

    d.rounded_rectangle([x, BOX_Y, x + BOX_W, BOX_Y + BOX_H], radius=14, fill=fill)

    # 번호
    d.text((x + 16, BOX_Y + 14), num, font=f(26), fill=sub)
    # 이름 (가운데)
    bb = d.textbbox((0, 0), name, font=f(36))
    d.text((x + (BOX_W - (bb[2] - bb[0])) // 2, BOX_Y + 62), name, font=f(36), fill=txt)
    # 산출물 (가운데, 두 줄 대응)
    words = out.split(' ')
    line1, line2 = out, ''
    if d.textbbox((0, 0), out, font=f(22))[2] > BOX_W - 20:
        mid = len(words) // 2 + 1
        line1 = ' '.join(words[:mid])
        line2 = ' '.join(words[mid:])
    for k, ln in enumerate([line1, line2]):
        if not ln:
            continue
        bb = d.textbbox((0, 0), ln, font=f(22))
        d.text((x + (BOX_W - (bb[2] - bb[0])) // 2, BOX_Y + 122 + k * 30), ln, font=f(22), fill=sub)

    # 화살표
    if i < N - 1:
        ax = x + BOX_W + 4
        ay = BOX_Y + BOX_H // 2
        d.polygon([(ax, ay - 9), (ax + GAP - 8, ay), (ax, ay + 9)], fill=(190, 194, 202))

# ── 1~7단계 3초 브래킷
b_x0 = MARGIN
b_x1 = MARGIN + 6 * (BOX_W + GAP) + BOX_W
b_y = BOX_Y + BOX_H + 46
d.line([(b_x0, b_y), (b_x1, b_y)], fill=ACCENT, width=3)
d.line([(b_x0, b_y), (b_x0, b_y - 14)], fill=ACCENT, width=3)
d.line([(b_x1, b_y), (b_x1, b_y - 14)], fill=ACCENT, width=3)
label = '1~7단계 연산 응답 3초 이내'
bb = d.textbbox((0, 0), label, font=f(30))
d.text(((b_x0 + b_x1 - (bb[2] - bb[0])) // 2, b_y + 14), label, font=f(30), fill=ACCENT)

# ── 8단계 순환 표시
loop_x = MARGIN + 7 * (BOX_W + GAP) + BOX_W // 2
d.text((loop_x - 130, b_y + 14), '→ 다시 4단계로 반영', font=f(26), fill=SUB)

# ── 범례
ly = H - 110
d.rounded_rectangle([MARGIN, ly, MARGIN + 34, ly + 26], radius=6, fill=NAVY)
d.text((MARGIN + 48, ly - 2), '본 사업에서 개발', font=f(28), fill=INK)
d.rounded_rectangle([MARGIN + 330, ly, MARGIN + 364, ly + 26], radius=6, fill=GRAY)
d.text((MARGIN + 378, ly - 2), '기보유 · 상용 프로젝트 검증 완료', font=f(28), fill=INK)

d.text((MARGIN, H - 54),
       '※ 얼굴 원본은 9단계에서 파기되며 익명 수치만 로컬에 저장된다. 전 단계 연산이 현장 장비에서 이루어진다.',
       font=f(25), fill=FAINT)

img.save('/home/user/art-grants-alert/references/figures/fig_pipeline_9step.png')
print('saved')
