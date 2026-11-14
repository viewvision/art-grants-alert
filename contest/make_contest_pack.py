# Contest winner pack: thumbnail (16:9), intro overlay (9:16, transparent) and ending card (9:16)
# in the look of the "2026 숏폼 영상 공모전" poster (paper grey, navy, viewfinder marks).
import json, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = "../shorts/fonts/"
L_, R_, B_, EB_ = (FD + f for f in ("NanumSquareL.ttf", "NanumSquareR.ttf", "NanumSquareB.ttf", "NanumSquareEB.ttf"))
NAVY = (34, 64, 152)
PAPER = (232, 232, 230)
WHITE = (255, 255, 255)
AWARD = {"대상": "대상", "금": "금상", "은": "은상", "동": "동상"}
CONTEST = "2026 숏폼 영상 공모전"
SLOGAN = "건축엔 건축사가 있습니다"
HOST = "주관 | 서울특별시건축사회 홍보위원회"
LINKS = "www.sira.or.kr   ·   Instagram @kiro_seoul"

def font(p, s): return ImageFont.truetype(p, s)

def paper(w, h):
    """Light grey paper with faint grain, like the poster background."""
    random.seed(7)
    base = Image.new("L", (w // 4, h // 4))
    base.putdata([random.randint(-9, 9) + 128 for _ in range(base.width * base.height)])
    grain = base.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
    img = Image.new("RGB", (w, h), PAPER)
    shade = Image.merge("RGB", [grain] * 3)
    return Image.blend(img, shade, 0.06)

def cross(d, x, y, s, col, w=2):
    d.line([(x - s, y), (x + s, y)], fill=col, width=w)
    d.line([(x, y - s), (x, y + s)], fill=col, width=w)

def corners(d, W, H, m, s, col, w=2):
    for x, y in ((m, m), (W - m, m), (m, H - m), (W - m, H - m)):
        cross(d, x, y, s, col, w)

def badge(d, x, y, text, size, fill=NAVY, fg=WHITE, pad=(22, 10)):
    f = font(EB_, size)
    tw = d.textlength(text, font=f)
    d.rectangle((x, y, x + tw + pad[0] * 2, y + size + pad[1] * 2), fill=fill)
    d.text((x + pad[0], y + pad[1] - 2), text, font=f, fill=fg)
    return x + tw + pad[0] * 2

def wrap(d, text, f, maxw):
    """Split title on ': ' first, then greedily by words, so long titles fit."""
    parts = [p for p in text.replace(": ", ":\n").split("\n")]
    lines = []
    for p in parts:
        cur = ""
        for word in p.split(" "):
            t = (cur + " " + word).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: lines.append(cur); cur = word
        lines.append(cur)
    return [l for l in lines if l]

def logo_slot(d, x, y, col, size=30):
    """Placeholder until the real logo file is supplied: outlined mark + wordmark."""
    s = int(size * 1.25)
    d.rectangle((x, y, x + s, y + s), outline=col, width=3)
    d.text((x + s // 2, y + s // 2), "LOGO", font=font(B_, int(size * 0.38)), fill=col, anchor="mm")
    d.text((x + s + 14, y + (s - size) // 2 - 2), "서울특별시건축사회", font=font(B_, size), fill=col)

def ending_916(w, out):
    W, H = 1080, 1920
    im = paper(W, H); d = ImageDraw.Draw(im)
    corners(d, W, H, 70, 26, NAVY)
    d.text((110, 110), "SHORT FORM\nVIDEO CONTEST", font=font(B_, 26), fill=NAVY, spacing=6)
    d.text((W - 110, 110), "ARCHITECTURE\n& ARCHITECT", font=font(B_, 26), fill=NAVY, spacing=6, anchor="ra", align="right")
    d.ellipse((W - 128, 210, W - 112, 226), fill=(225, 40, 40)); d.text((W - 140, 206), "REC", font=font(B_, 24), fill=NAVY, anchor="ra")
    # award + contest
    y = 470
    x = badge(d, 110, y, AWARD[w["award"]], 56)
    d.text((x + 24, y + 22), CONTEST, font=font(B_, 40), fill=NAVY)
    # title
    tf = font(EB_, 92)
    lines = wrap(d, w["title"], tf, W - 220)
    y = 620
    for l in lines:
        d.text((110, y), l, font=tf, fill=NAVY); y += 118
    d.line([(110, y + 20), (W - 110, y + 20)], fill=NAVY, width=2)
    who = w["team"] + (f"  ({w['members']})" if w["members"] else "")
    d.text((110, y + 50), "제작", font=font(R_, 36), fill=NAVY)
    d.text((210, y + 50), who, font=font(B_, 40), fill=NAVY)
    # slogan block
    sy = 1330
    d.rectangle((110, sy, W - 110, sy + 190), fill=NAVY)
    d.text((W // 2, sy + 95), SLOGAN, font=font(EB_, 64), fill=WHITE, anchor="mm")
    # footer
    d.text((110, 1610), HOST, font=font(R_, 32), fill=NAVY)
    d.text((110, 1660), LINKS, font=font(R_, 30), fill=NAVY)
    logo_slot(d, 110, 1740, NAVY, 34)
    im.save(out, quality=95)

def intro_916(w, out):
    """Transparent overlay for the first ~2 s; also works as the Shorts cover frame."""
    W, H = 1080, 1920
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    corners(d, W, H, 70, 26, WHITE + (230,), 3)
    d.ellipse((W - 128, 112, W - 112, 128), fill=(235, 45, 45, 255)); d.text((W - 140, 108), "REC", font=font(B_, 26), fill=WHITE, anchor="ra")
    # top info panel
    tf = font(EB_, 84)
    lines = wrap(d, w["title"], tf, W - 220)
    ph = 250 + len(lines) * 104 + 80
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(panel)
    pd.rectangle((70, 180, W - 70, 180 + ph), fill=NAVY + (225,))
    im = Image.alpha_composite(im, panel); d = ImageDraw.Draw(im)
    x = badge(d, 110, 220, AWARD[w["award"]], 48, fill=WHITE, fg=NAVY)
    d.text((x + 22, 238), CONTEST, font=font(B_, 36), fill=WHITE)
    y = 330
    for l in lines:
        d.text((110, y), l, font=tf, fill=WHITE); y += 104
    who = w["team"] + (f"  ({w['members']})" if w["members"] else "")
    d.text((110, y + 20), who, font=font(R_, 38), fill=WHITE)
    logo_slot(d, 110, H - 200, WHITE, 30)
    im.save(out)

def thumb_169(w, out):
    """16:9 thumbnail; the FRAME window is transparent so a video still can sit behind it."""
    W, H = 1280, 720
    im = paper(W, H).convert("RGBA"); d = ImageDraw.Draw(im)
    corners(d, W, H, 34, 14, NAVY)
    fx0, fy0, fx1, fy1 = 640, 70, 1220, 650
    hole = Image.new("L", (W, H), 255); ImageDraw.Draw(hole).rectangle((fx0, fy0, fx1, fy1), fill=0)
    im.putalpha(hole); d = ImageDraw.Draw(im)
    d.rectangle((fx0, fy0, fx1, fy1), outline=NAVY, width=4)
    d.text((fx0 + 16, fy0 + 12), "FRAME 01", font=font(B_, 18), fill=WHITE)
    d.text((70, 64), "SHORT FORM VIDEO CONTEST", font=font(B_, 18), fill=NAVY)
    x = badge(d, 70, 130, AWARD[w["award"]], 46)
    d.text((x + 18, 146), CONTEST, font=font(B_, 28), fill=NAVY)
    tf = font(EB_, 64)
    lines = wrap(d, w["title"], tf, 540)
    y = 240
    for l in lines:
        d.text((70, y), l, font=tf, fill=NAVY); y += 82
    who = w["team"] + (f" ({w['members']})" if w["members"] else "")
    d.text((70, y + 22), who, font=font(B_, 28), fill=NAVY)
    logo_slot(d, 70, 610, NAVY, 26)
    im.save(out)

if __name__ == "__main__":
    w = json.loads(sys.argv[1]); tag = sys.argv[2]
    thumb_169(w, f"{tag}_thumb_16x9.png")
    intro_916(w, f"{tag}_intro_9x16.png")
    ending_916(w, f"{tag}_ending_9x16.png")
    print("done", tag)
