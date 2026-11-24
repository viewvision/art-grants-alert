"""Title mockups for scene 1: '배보다 배꼽'"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = '/home/user/art-grants-alert/shorts/fonts/'
base = Image.open('/home/user/art-grants-alert/shorts/title/scene1_frame.jpg').convert('RGBA')
W, H = base.size
YEL = (255, 214, 0); ORG = (255, 122, 26); BLK = (20, 20, 20); WHT = (255, 255, 255)

def shadow(layer, off=(0, 8), blur=10, alpha=90):
    a = layer.split()[3].point(lambda v: v * alpha // 255)
    s = Image.new('RGBA', layer.size, (0, 0, 0, 0)); s.putalpha(a)
    s = s.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new('RGBA', layer.size, (0, 0, 0, 0)); out.alpha_composite(s, off); out.alpha_composite(layer)
    return out

def runs_width(d, runs, font):
    return sum(d.textlength(t, font=font) for t, _ in runs)

def draw_runs(d, x, y, runs, font, stroke=0, sc=BLK):
    for t, c in runs:
        d.text((x, y), t, font=font, fill=c, stroke_width=stroke, stroke_fill=sc)
        x += d.textlength(t, font=font)

# A: white bold text + thick black outline (matches character line art), '배꼽' in yellow
def style_a():
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    f = ImageFont.truetype(F + 'NanumSquareEB.ttf', 150)
    runs = [('배보다 ', WHT), ('배꼽', YEL)]
    w = runs_width(d, runs, f); x = (W - w) / 2
    draw_runs(d, x, 150, runs, f, stroke=14)
    sub = ImageFont.truetype(F + 'NanumSquareB.ttf', 46)
    t = '건물 매입 전, 꼭 확인해야 할 것'
    d.text(((W - d.textlength(t, font=sub)) / 2, 340), t, font=sub, fill=WHT, stroke_width=7, stroke_fill=BLK)
    return shadow(L)

# B: rounded orange label box with white text (same family as speech bubbles)
def style_b():
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    f = ImageFont.truetype(F + 'NanumSquareRoundB.ttf', 120)
    t = '배보다 배꼽'
    tw = d.textlength(t, font=f); bw, bh = tw + 120, 200; x0 = (W - bw) / 2; y0 = 150
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 40, fill=ORG, outline=BLK, width=8)
    d.text(((W - tw) / 2, y0 + 30), t, font=f, fill=WHT)
    sub = ImageFont.truetype(F + 'NanumSquareB.ttf', 44)
    s = '건물 매입 전, 꼭 확인해야 할 것'; sw = d.textlength(s, font=sub)
    d.rounded_rectangle(((W - sw) / 2 - 30, y0 + bh + 24, (W + sw) / 2 + 30, y0 + bh + 104), 20, fill=WHT, outline=BLK, width=6)
    d.text(((W - sw) / 2, y0 + bh + 38), s, font=sub, fill=BLK)
    return shadow(L)

# C: construction caution tape band (architecture theme), black text on yellow
def style_c():
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    y0, bh = 150, 230
    band = Image.new('RGBA', (W + 200, bh), YEL + (255,)); bd = ImageDraw.Draw(band)
    for i in range(-bh, W + 400, 70):
        bd.polygon([(i, 0), (i + 35, 0), (i + 35 - bh * 0 + 0, 0)], fill=BLK)
    for i in range(-bh, W + 400, 80):
        bd.polygon([(i, bh), (i + 40, bh), (i + 40 + 30, bh - 30), (i + 30, bh - 30)], fill=BLK)
        bd.polygon([(i, 0), (i + 40, 0), (i + 70, 30), (i + 30, 30)], fill=BLK)
    bd.line((0, 0, W + 200, 0), fill=BLK, width=8); bd.line((0, bh - 1, W + 200, bh - 1), fill=BLK, width=8)
    band = band.rotate(-3, expand=True, resample=Image.BICUBIC)
    L.alpha_composite(band, (-100, y0 - 40))
    f = ImageFont.truetype(F + 'NanumSquareEB.ttf', 130)
    t = '배보다 배꼽'; tw = d.textlength(t, font=f)
    tl = Image.new('RGBA', (W, H)); td = ImageDraw.Draw(tl)
    td.text(((W - tw) / 2, y0 + 25), t, font=f, fill=BLK)
    tl = tl.rotate(-3, center=(W / 2, y0 + 100), resample=Image.BICUBIC)
    L.alpha_composite(tl)
    return shadow(L, blur=8, alpha=70)

outs = []
for name, fn in [('A', style_a), ('B', style_b), ('C', style_c)]:
    im = base.copy(); im.alpha_composite(fn())
    im.convert('RGB').save(f'/home/user/art-grants-alert/shorts/title/title_{name}.jpg', quality=92)
    outs.append(im.convert('RGB').resize((W // 2, H // 2)))
sheet = Image.new('RGB', (W // 2 * 3 + 40, H // 2), 'white')
for i, o in enumerate(outs): sheet.paste(o, (i * (W // 2 + 20), 0))
sheet.save('/home/user/art-grants-alert/shorts/title/title_compare.jpg', quality=90)
