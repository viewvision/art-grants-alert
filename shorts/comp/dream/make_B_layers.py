"""B안(생각 구름 프레임) AE용 레이어 PNG, 1080x1920. 큼직한 구름 버전."""
import numpy as np, cv2, math
from PIL import Image, ImageDraw, ImageFilter
import sys; sys.path.insert(0, 'comp/dream')
W, H = 1080, 1920; OUT = 'comp/dream/B_layers/'
import os; os.makedirs(OUT, exist_ok=True)

def dreamy(img, glow=0.3):
    a = np.asarray(img).astype(np.float32) / 255
    b = cv2.GaussianBlur(a, (0, 0), 28); a = 1 - (1 - a) * (1 - b * glow)
    a = a * 1.06 + 0.03; g = a.mean(2, keepdims=True); a = g + (a - g) * 0.85
    a = a * np.array([1.03, 1.0, 0.94])
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

# 큼직한 구름: 적은 개수의 큰 원, 크기 교대로
cx, cy, rx, ry = W / 2, 960, 300, 700
sizes = [215, 185, 210, 190, 215, 185, 215, 190, 210, 185, 215, 190]
SS = 2  # 슈퍼샘플링으로 매끈한 외곽
m = Image.new('L', (W * SS, H * SS), 0); d = ImageDraw.Draw(m)
d.ellipse(((cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS), fill=255)
n = len(sizes)
for i, r in enumerate(sizes):
    t = 2 * math.pi * i / n - math.pi / 2
    x, y = cx + rx * math.cos(t), cy + ry * math.sin(t)
    d.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS), fill=255)
mask_hi = np.asarray(m)
ring = cv2.morphologyEx(mask_hi, cv2.MORPH_GRADIENT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (22, 22)))
mask = Image.fromarray(mask_hi).resize((W, H), Image.LANCZOS)
line = Image.fromarray(ring).resize((W, H), Image.LANCZOS)

def rgba(colour, alpha):
    im = Image.new('RGBA', (W, H), colour + (255,)); im.putalpha(alpha); return im

# 1 구름 매트(안쪽 흰색) – AE 트랙 매트(Alpha)용
rgba((255, 255, 255), mask).save(OUT + '01_cloud_matte.png')
# 2 구름 바깥 배경(연보라) – 구름 자리는 뚫림
rgba((238, 236, 244), Image.fromarray(255 - np.asarray(mask))).save(OUT + '02_outside_fill.png')
# 3 구름 외곽선
rgba((20, 20, 20), line).save(OUT + '03_cloud_outline.png')
# 4 생각 꼬리 동그라미 (왼쪽 아래 → 의뢰인 쪽)
t = Image.new('RGBA', (W * SS, H * SS)); d = ImageDraw.Draw(t)
for (x, y, r) in [(60, 1880, 20), (115, 1815, 30), (180, 1730, 42)]:
    d.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS), fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=9 * SS)
t.resize((W, H), Image.LANCZOS).save(OUT + '04_thought_tail.png')
# 5 몽환 보정된 배경 (전체 프레임) – 01을 매트로 사용
bg = dreamy(Image.open('comp/dream/bg_cafe_1080.jpg').convert('RGB'))
bg.save(OUT + '05_bg_dreamy.png')
bg.putalpha(mask); bg.save(OUT + '05b_bg_dreamy_cut.png')   # 매트 없이 바로 쓰는 버전

# 미리보기
pv = Image.open(OUT + '02_outside_fill.png').copy()
pv = Image.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 0)), pv)
for f in ['05b_bg_dreamy_cut.png', '03_cloud_outline.png', '04_thought_tail.png']:
    pv = Image.alpha_composite(pv, Image.open(OUT + f))
pv = Image.alpha_composite(pv, Image.open('comp/dream/fg_chars_bubble.png').convert('RGBA'))
pv.convert('RGB').save('comp/dream/mock_B2_preview.jpg', quality=92)
