from PIL import Image, ImageDraw, ImageFont
import colorsys

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def f(sz):
    return ImageFont.truetype(FONT, sz)

BG = (250, 249, 246)
INK = (28, 34, 48)
SUB = (110, 118, 132)
LINE = (222, 220, 214)

# 원소별 최고강도 기준색 (문서의 색 서술과 일치)
ELEMENTS = [
    ('물',  '청록 · 시안',        (0, 158, 176), '내면으로 가라앉음', '가라앉으며 고인다'),
    ('불',  '코랄 · 주황빛 골드',  (238, 104,  54), '밖으로 터져 나감',  '피어오르며 번진다'),
    ('공기', '옅은 라벤더',        (140, 124, 200), '아직 오지 않은 것', '경계 없이 흩어진다'),
    ('흙',  '따뜻한 황토 · 호박',  (186, 134,  48), '현재에 머묾',       '구조를 이루며 응집한다'),
]
STEPS = ['저', '중', '고']

def mix(c, t):
    """t=0이면 배경에 가깝게(저채도), t=1이면 원색"""
    return tuple(int(BG[i] + (c[i] - BG[i]) * t) for i in range(3))

W, H = 2000, 1330
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

# ── 헤더
d.text((70, 58), '4가지 방향 — 판정 결과가 곧 색이 된다', font=f(52), fill=INK)
d.text((70, 128),
       '강도(arousal)는 채도로, 톤(valence)은 밝기와 번지는 방향으로 옮겨진다.',
       font=f(30), fill=SUB)
d.line([(70, 190), (W - 70, 190)], fill=INK, width=3)

# ── 컬럼 헤더
col_x = [70, 470, 760, 1050, 1340, 1700]   # 원소 / 저 / 중 / 고 / (여백) / 운동성질
d.text((470, 214), '강도 저', font=f(28), fill=SUB)
d.text((760, 214), '강도 중', font=f(28), fill=SUB)
d.text((1050, 214), '강도 고', font=f(28), fill=SUB)
d.text((1400, 214), '화면 위 운동 성질', font=f(28), fill=SUB)

ROW_TOP = 262
ROW_H = 218
SW_W, SW_H = 250, 132

for i, (name, desc, base, axis, motion) in enumerate(ELEMENTS):
    y = ROW_TOP + i * ROW_H

    # 원소명 + 색 이름
    d.text((70, y + 26), name, font=f(56), fill=INK)
    d.text((70, y + 96), desc, font=f(27), fill=SUB)
    d.text((70, y + 136), axis, font=f(25), fill=(160, 166, 178))

    # 3단계 스와치
    for j, t in enumerate([0.32, 0.66, 1.0]):
        x = col_x[1 + j]
        c = mix(base, t)
        d.rounded_rectangle([x, y + 20, x + SW_W, y + 20 + SW_H], radius=10, fill=c)
        hexs = '#%02X%02X%02X' % c
        d.text((x, y + 20 + SW_H + 14), hexs, font=f(24), fill=SUB)

    # 운동 성질
    d.text((1400, y + 66), motion, font=f(34), fill=INK)

    if i < len(ELEMENTS) - 1:
        d.line([(70, y + ROW_H - 22), (W - 70, y + ROW_H - 22)], fill=LINE, width=2)

# ── 하단 주석
d.line([(70, H - 150), (W - 70, H - 150)], fill=INK, width=3)
d.text((70, H - 126),
       '한 화면에는 판정 결과 상위 두 방향만 나타난다. 배경색은 1위 방향의 보색 계열로 자동 결정된다.',
       font=f(29), fill=SUB)
d.text((70, H - 74),
       '※ 위 색값은 기준값이며, 실제 화면에서는 톤·강도 판정에 따라 연속적으로 변한다.',
       font=f(26), fill=(160, 166, 178))

img.save('/home/user/art-grants-alert/references/figures/fig_palette_4direction.png')
print('saved')
