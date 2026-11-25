"""상상씬 배경 효과 목업: A안(구름 비네트+글로우+반짝이), B안(생각 구름 프레임)."""
import numpy as np, cv2, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H = 1080, 1920
bg = Image.open('comp/dream/bg_cafe_1080.jpg').convert('RGB')
fg = Image.open('comp/dream/fg_chars_bubble.png').convert('RGBA')

def dreamy(img, glow=0.45, warm=True):
    a = np.asarray(img).astype(np.float32) / 255
    b = cv2.GaussianBlur(a, (0, 0), 28)
    a = 1 - (1 - a) * (1 - b * glow)            # screen
    a = a * 1.06 + 0.03                         # 노출 업
    g = a.mean(2, keepdims=True); a = g + (a - g) * 0.85   # 채도 살짝 다운
    if warm: a = a * np.array([1.03, 1.0, 0.94])
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

def cloud_mask(cx, cy, rx, ry, bump=95, n=26, seed=3):
    """타원 둘레에 원을 붙여 만든 구름 모양 (안쪽=255)."""
    rnd = random.Random(seed); m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    for i in range(n):
        t = 2 * math.pi * i / n; r = bump * rnd.uniform(0.8, 1.15)
        x, y = cx + rx * math.cos(t), cy + ry * math.sin(t)
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    return m

def sparkle(d, x, y, r, a=230):
    c = (255, 252, 235, a)
    d.polygon([(x, y - r), (x + r * .18, y - r * .18), (x + r, y), (x + r * .18, y + r * .18),
               (x, y + r), (x - r * .18, y + r * .18), (x - r, y), (x - r * .18, y - r * .18)], fill=c)

def coin(d, x, y, r, font):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 205, 40, 255), outline=(20, 20, 20, 255), width=5)
    d.ellipse((x - r * .72, y - r * .72, x + r * .72, y + r * .72), outline=(200, 140, 0, 255), width=4)
    d.text((x, y + 2), '₩', font=font, fill=(20, 20, 20, 255), anchor='mm')

font = ImageFont.truetype(next(__import__('glob').iglob('fonts/*.[ot]tf')), 44)

# ---------- A안 ----------
A = dreamy(bg).convert('RGBA')
cm = cloud_mask(W / 2, H / 2 + 40, 430, 830, bump=120, n=30).filter(ImageFilter.GaussianBlur(55))
white = Image.new('RGBA', (W, H), (255, 253, 247, 255))
A = Image.composite(A, white, cm)
fx = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(fx); rnd = random.Random(7)
for _ in range(16):
    sparkle(d, rnd.uniform(80, W - 80), rnd.uniform(250, 1500), rnd.uniform(10, 30), rnd.randint(150, 240))
A = Image.alpha_composite(A, fx.filter(ImageFilter.GaussianBlur(1.5)))
cl = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(cl)
for (x, y, r) in [(560, 1040, 40), (950, 1300, 34), (130, 1380, 36), (470, 1600, 30), (880, 760, 30)]:
    coin(d, x, y, r, font)
A = Image.alpha_composite(A, cl)
A_bg = A.copy()
A = Image.alpha_composite(A, fg)
A.convert('RGB').save('comp/dream/mock_A.jpg', quality=92)

# ---------- B안 ----------
outside = Image.new('RGBA', (W, H), (238, 236, 244, 255))
inner = dreamy(bg, glow=0.3).convert('RGBA')
cm = cloud_mask(W / 2, 1020, 440, 700, bump=105, n=24, seed=5)
B = Image.composite(inner, outside, cm.filter(ImageFilter.GaussianBlur(1.2)))
edge = cv2.morphologyEx(np.asarray(cm), cv2.MORPH_GRADIENT, np.ones((9, 9), np.uint8))
ol = Image.new('RGBA', (W, H), (20, 20, 20, 255)); ol.putalpha(Image.fromarray(edge).filter(ImageFilter.GaussianBlur(0.8)))
B = Image.alpha_composite(B, ol)
d = ImageDraw.Draw(B)   # 생각 꼬리 동그라미 (화면 아래 왼쪽 = 의뢰인 머리 쪽에서 이어짐)
for (x, y, r) in [(110, 1830, 22), (170, 1760, 32), (250, 1680, 44)]:
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=8)
B_bg = B.copy()
B = Image.alpha_composite(B, fg)
B.convert('RGB').save('comp/dream/mock_B.jpg', quality=92)

cmp = Image.new('RGB', (W * 3 // 2 + 40, H // 2 + 60), 'white')
for i, im in enumerate([Image.open('comp/dream/user_comp.jpg'), A, B]):
    cmp.paste(im.convert('RGB').resize((W // 2, H // 2)), (i * (W // 2 + 20), 60))
dd = ImageDraw.Draw(cmp); f2 = ImageFont.truetype(font.path, 36)
for i, t in enumerate(['원본', 'A안', 'B안']): dd.text((i * (W // 2 + 20) + 20, 12), t, font=f2, fill='black')
cmp.save('comp/dream/mock_compare.jpg', quality=90)
