"""F_steel_final_topaz2x.png 에서 철골 기둥(+보)만 남기고 투명 처리. 바닥 접지 그림자 별도 추출."""
import numpy as np, cv2
from PIL import Image
SRC = 'bg/F_steel_final_topaz2x.png'; OUT = 'comp/steel/'
img = np.array(Image.open(SRC).convert('RGB')); H, W = img.shape[:2]
a = img.astype(np.float32)
blue = cv2.GaussianBlur(a[..., 2] - a[..., 0], (0, 0), 4)
steel = blue > 6
g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
mu = cv2.blur(g, (9, 9)); sd = np.sqrt(np.maximum(cv2.blur(g * g, (9, 9)) - mu * mu, 0))
steel_h = steel & (cv2.GaussianBlur(sd, (0, 0), 3) < 3.8)   # 보: 매끈한 면만 (골판 천장 제외)

def fit(v, deg=2, it=4):
    """직선/완만한 곡선으로 강건 피팅 (천장 골판 등 튀는 값 제거)."""
    i = np.arange(len(v)); ok = v >= 0
    for _ in range(it):
        c = np.polyfit(i[ok], v[ok], deg); r = v - np.polyval(c, i)
        sd = np.std(r[ok]); ok = (v >= 0) & (np.abs(r) < max(2.5 * sd, 3))
    out = np.polyval(c, i); return out, i[ok].min(), i[ok].max()

def med(v, k=61):
    v = v.astype(np.float32); out = v.copy(); h = k // 2
    for i in range(len(v)):
        w = v[max(0, i - h):i + h + 1]; w = w[w >= 0]
        out[i] = np.median(w) if len(w) else -1
    return out

def vertical(x0, x1, y0, y1, base=110):
    """세로 부재: 행마다 좌우 경계."""
    m = np.zeros((H, W), np.uint8)
    L = np.full(H, -1.0); R = np.full(H, -1.0)
    for y in range(y0, y1):
        xs = np.where(steel[y, x0:x1])[0]
        if len(xs) > 10: L[y] = x0 + np.percentile(xs, 2); R[y] = x0 + np.percentile(xs, 98)
    Ls, a0, a1 = fit(L[y0:y1], 1); Rs, b0, b1 = fit(R[y0:y1], 1)
    valid = np.where(L[y0:y1] >= 0)[0]; last = valid.max()
    Lr, Rr = med(L[y0:y1], 9), med(R[y0:y1], 9)
    for i, y in enumerate(range(y0, y1)):
        if i > last: break
        l, r = Ls[i], Rs[i]
        if i > last - base and Lr[i] >= 0:      # 밑판(베이스 플레이트)은 실제 윤곽
            l, r = min(l, Lr[i]), max(r, Rr[i])
        m[y, int(round(l)):int(round(r)) + 1] = 255
    return m

def horizontal(x0, x1, y0, y1):
    """가로 부재: 열마다 위아래 경계."""
    m = np.zeros((H, W), np.uint8)
    T = np.full(W, -1.0); B = np.full(W, -1.0)
    for x in range(x0, x1):
        ys = np.where(steel_h[y0:y1, x])[0]
        if len(ys) > 10: T[x] = y0 + np.percentile(ys, 2); B[x] = y0 + np.percentile(ys, 98)
    Ts, a0, a1 = fit(T[x0:x1], 2); Bs, b0, b1 = fit(B[x0:x1], 2)
    # 플랜지까지 포함하도록 경계를 실제 밝기 경계(세로 그라디언트 최대)로 다시 맞춤
    gy = np.abs(cv2.Sobel(cv2.GaussianBlur(g, (0, 0), 2), cv2.CV_32F, 0, 1, ksize=5))
    T2 = np.full(x1 - x0, -1.0); B2 = np.full(x1 - x0, -1.0)
    for i, x in enumerate(range(x0, x1)):
        t, b = int(Ts[i]), int(Bs[i])
        ta, tb = max(0, t - 45), t + 6; ba_, bb = b - 6, min(H - 1, b + 35)
        T2[i] = ta + np.argmax(gy[ta:tb, x]); B2[i] = ba_ + np.argmax(gy[ba_:bb, x])
    Ts, _, _ = fit(T2, 2); Bs, _, _ = fit(B2, 2)
    lo, hi = max(a0, b0), min(a1, b1)
    for i, x in enumerate(range(x0, x1)):
        if lo <= i <= hi: m[int(round(Ts[i])):int(round(Bs[i])) + 1, x] = 255
    return m

cols = vertical(110, 360, 1190, 2700) | vertical(1880, 2140, 1170, 2690)
beams = (horizontal(0, W, 330, 660) | horizontal(0, W, 1020, 1230) |
         horizontal(290, 1960, 1360, 1510) | horizontal(460, 1790, 1560, 1690))

def save(mask, name):
    al = cv2.GaussianBlur(mask, (0, 0), 0.8)
    rgba = np.dstack([img, al]); Image.fromarray(rgba).save(OUT + name)
    return al

ca = save(cols, 'steel_columns.png')
ba = save(beams & ~cols, 'steel_beams.png')
save(cols | beams, 'steel_columns_beams.png')

# 바닥 접지 그림자: 기둥 밑판 주변에서 주변보다 어두운 부분
L = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
ref = cv2.medianBlur(L.astype(np.uint8), 61).astype(np.float32)
dark = np.clip((ref - L - 4) / 35, 0, 1)
dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((25, 25), np.uint8))  # 바닥 잔해 점 제거
zone = np.zeros((H, W), np.uint8)
for (x0, x1, yb) in [(110, 360, 2670), (1880, 2140, 2660)]:
    cv2.ellipse(zone, ((x0 + x1) // 2, yb), ((x1 - x0) // 2 + 120, 70), 0, 0, 360, 255, -1)
zone = cv2.GaussianBlur(zone, (0, 0), 25).astype(np.float32) / 255
sh = cv2.GaussianBlur(dark, (0, 0), 10) * zone * (1 - cols / 255.0)
soft = np.zeros((H, W), np.float32)
for (cx, yb, rx) in [(225, 2684, 125), (2020, 2664, 120)]:
    cv2.ellipse(soft, (cx, yb - 6), (rx, 22), 0, 0, 360, 1.0, -1)
soft = cv2.GaussianBlur(soft, (0, 0), 16) * 0.38
sh = np.maximum(sh, soft) * (1 - cols / 255.0)
sh_a = (np.clip(sh * 1.2, 0, 0.85) * 255).astype(np.uint8)
shadow = np.zeros((H, W, 4), np.uint8); shadow[..., :3] = (25, 25, 28); shadow[..., 3] = sh_a
Image.fromarray(shadow).save(OUT + 'steel_column_shadow.png')

# 미리보기 (체커/흰 배경 위)
for name in ['steel_columns', 'steel_columns_beams']:
    fg = Image.open(OUT + name + '.png'); bgc = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    bgc.alpha_composite(Image.open(OUT + 'steel_column_shadow.png')); bgc.alpha_composite(fg)
    bgc.convert('RGB').resize((W // 4, H // 4)).save(OUT + name + '_preview.jpg', quality=90)
