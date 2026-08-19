from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def f(sz):
    return ImageFont.truetype(FONT, sz)

BG   = (250, 249, 246)
INK  = (28, 34, 48)
SUB  = (110, 118, 132)
FAINT= (170, 176, 186)
DIM  = (205, 208, 214)

W, H = 2000, 1530
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

# ── 헤더
d.text((70, 54), '출력 사양 — 왜 2.2m × 2.93m인가', font=f(50), fill=INK)
d.text((70, 122),
       '전신 실루엣이 실제 사람 크기로 맺히려면 상지 도달 높이를 화면 상단 기준으로 삼아야 한다.',
       font=f(28), fill=SUB)
d.line([(70, 178), (W - 70, 178)], fill=INK, width=3)

# ── 패널 좌표 (2.93 : 2.20 = 4:3)
PX, PY = 300, 300          # 패널 좌상단
PW = 1020                  # 패널 폭 (px)
PH = int(PW * 2.20 / 2.93) # 높이 = 766
PANEL = [PX, PY, PX + PW, PY + PH]

M_PER_PX = 2.93 / PW       # 미터/픽셀

# 패널 화면 (밝은 배경 — 실제 작품 원칙과 일치)
d.rectangle(PANEL, fill=(232, 240, 246), outline=(190, 196, 204), width=3)

# 미세한 픽셀 그리드 (파인피치 느낌)
for gx in range(PX, PX + PW, 6):
    d.line([(gx, PY), (gx, PY + PH)], fill=(226, 235, 242), width=1)

# ── 인물 실루엣 169cm
h_m = 1.69
fig_h = int(h_m / M_PER_PX)
base_y = PY + PH - 6                 # 발이 화면 하단
top_y  = base_y - fig_h
cx     = PX + PW // 2

SIL = (150, 162, 176)
head_r = int(fig_h * 0.055)
head_cy = top_y + head_r
d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=SIL)
# 몸통
tw = int(fig_h * 0.115)
ty0 = head_cy + head_r + int(fig_h * 0.015)
ty1 = top_y + int(fig_h * 0.55)
d.rounded_rectangle([cx - tw, ty0, cx + tw, ty1], radius=int(tw*0.5), fill=SIL)
# 팔
aw = int(fig_h * 0.032)
d.rounded_rectangle([cx - tw - aw*2, ty0 + int(fig_h*0.01), cx - tw - 2, ty1 - int(fig_h*0.02)],
                    radius=aw, fill=SIL)
d.rounded_rectangle([cx + tw + 2, ty0 + int(fig_h*0.01), cx + tw + aw*2, ty1 - int(fig_h*0.02)],
                    radius=aw, fill=SIL)
# 다리
lw = int(fig_h * 0.042)
d.rounded_rectangle([cx - tw + 4, ty1 - int(fig_h*0.02), cx - tw + 4 + lw*2, base_y], radius=lw, fill=SIL)
d.rounded_rectangle([cx + tw - 4 - lw*2, ty1 - int(fig_h*0.02), cx + tw - 4, base_y], radius=lw, fill=SIL)

# ── 상지 도달 높이 기준선 (169cm × 1.24 ≒ 2.10m)
reach_m = 2.10
reach_y = base_y - int(reach_m / M_PER_PX)
d.line([(PX - 30, reach_y), (PX + PW + 30, reach_y)], fill=(214, 96, 60), width=3)
d.text((PX + PW + 44, reach_y - 44),
       '상지 도달 높이', font=f(26), fill=(214, 96, 60))
d.text((PX + PW + 44, reach_y - 6),
       '약 2.10m', font=f(30), fill=(214, 96, 60))

# ── 치수선: 가로
dy = PY - 62
d.line([(PX, dy), (PX + PW, dy)], fill=INK, width=3)
for xx in (PX, PX + PW):
    d.line([(xx, dy - 14), (xx, dy + 14)], fill=INK, width=3)
d.text((PX + PW // 2 - 90, dy - 62), '2.93 m (W)', font=f(38), fill=INK)

# ── 치수선: 세로
dx = PX - 86
d.line([(dx, PY), (dx, PY + PH)], fill=INK, width=3)
for yy in (PY, PY + PH):
    d.line([(dx - 14, yy), (dx + 14, yy)], fill=INK, width=3)
d.text((70, PY + PH // 2 - 24), '2.20 m', font=f(38), fill=INK)
d.text((70, PY + PH // 2 + 22), '(H)', font=f(30), fill=SUB)

# ── 인물 키 표기
d.text((cx + int(tw*2.4), base_y - int(fig_h*0.42)), '169 cm', font=f(28), fill=(120, 130, 145))
d.text((cx + int(tw*2.4), base_y - int(fig_h*0.42) + 38), '20대 평균 신장', font=f(24), fill=FAINT)

# ── 하단 사양 요약
by = PY + PH + 96
d.line([(70, by - 34), (W - 70, by - 34)], fill=INK, width=3)

rows = [
    ('출력', '파인피치 LED 디스플레이', '2.2m(H) × 2.93m(W), 4:3 / 화소피치 P1.2~1.5mm',
     '근접 0.5~1m에서 픽셀 비가시급'),
    ('입력', '깊이 센싱 카메라 (Kinect DK)', 'RGB 4K · 30fps, 수평화각 약 90°',
     '1대로 전신 + 얼굴 크롭 동시 처리'),
    ('연산', '렌더링 · 추론 서버', 'GPU 탑재 로컬 워크스테이션',
     '인식 · 생성 · 렌더링 전부 현장 처리'),
]
col = [70, 180, 590, 1340]
d.text((col[0], by), '구분', font=f(26), fill=SUB)
d.text((col[1], by), '장비', font=f(26), fill=SUB)
d.text((col[2], by), '제안 사양', font=f(26), fill=SUB)
d.text((col[3], by), '선택 근거', font=f(26), fill=SUB)
d.line([(70, by + 44), (W - 70, by + 44)], fill=(222, 220, 214), width=2)

for i, (a, b, c, e) in enumerate(rows):
    y = by + 70 + i * 78
    d.text((col[0], y), a, font=f(30), fill=INK)
    d.text((col[1], y), b, font=f(28), fill=INK)
    d.text((col[2], y), c, font=f(27), fill=(70, 78, 92))
    d.text((col[3], y), e, font=f(25), fill=SUB)
    if i < len(rows) - 1:
        d.line([(70, y + 56), (W - 70, y + 56)], fill=(234, 232, 227), width=1)

d.text((70, H - 56),
       '※ 위 3종이 예산계획의 임차료 항목을 구성한다. 최종 사양은 착수 협의에서 현장 조건에 맞춰 확정한다.',
       font=f(25), fill=FAINT)

img.save('/home/user/art-grants-alert/references/figures/fig_hardware_scale.png')
print('saved')
