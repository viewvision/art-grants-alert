"""Flatten AI fill texture and remove motion ghosts.
usage: flatten.py in.mp4 ref.png out.mp4
 - palette (k-means) from the character reference image
 - pixel close to a palette colour -> snapped to that exact colour (kills blotches)
 - pale low-saturation pixels (ghost trails, specks) -> pure white
 - dark outline / anti-aliased edge pixels are left untouched
"""
import sys, subprocess, os, numpy as np, cv2
src, ref, out = sys.argv[1:4]
r = cv2.imread(ref); rl = cv2.cvtColor(r, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
keep = rl[:, 0] < 245  # ignore white background when building palette
smp = rl[keep][np.random.default_rng(0).choice(keep.sum(), min(150000, keep.sum()), replace=False)]
_, _, cent = cv2.kmeans(smp, 7, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 60, 0.5), 3, cv2.KMEANS_PP_CENTERS)
# keep only fill colours (drop the near-black outline cluster, outlines stay as-is)
cent = np.array([c for c in cent if c[0] > 60], np.float32)
pal = cv2.cvtColor(cent.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_LAB2BGR).reshape(-1, 3)
print('palette BGR', pal.tolist())
cap = cv2.VideoCapture(src); fps = cap.get(5); W = int(cap.get(3)); H = int(cap.get(4))
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
# motion-smear score: semi-transparent (pale, mid-saturation) pixels
def smear(f):
    h = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    return int(((h[..., 1] > 35) & (h[..., 1] < 150) & (h[..., 2] > 175)).sum())
sc = np.array([smear(f) for f in frames]); med = np.median(sc)
bad = sc > max(3 * med, med + 1500)
src_idx = list(range(len(frames)))
for i in range(len(frames)):
    if bad[i]:
        j = i
        while j > 0 and bad[j]: j -= 1
        if bad[j]:
            j = i
            while j < len(frames) - 1 and bad[j]: j += 1
        src_idx[i] = j
print('smear frames held:', int(bad.sum()), 'of', len(frames))
tmp = out + '.v.mp4'; vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (W, H))
for i in range(len(frames)):
    f = frames[src_idx[i]]
    lab = cv2.cvtColor(cv2.medianBlur(f, 5), cv2.COLOR_BGR2LAB).astype(np.float32)
    d = np.sqrt(((lab[:, :, None, :] - cent[None, None]) ** 2).sum(-1))
    k = d.argmin(-1); dm = d.min(-1)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    o = f.copy()
    snap = dm < 22
    o[snap] = pal[k[snap]]
    # ghosts/specks: bright & weakly saturated, not snapped to a fill colour
    ghost = (hsv[..., 2] > 185) & (hsv[..., 1] < 95) & ~snap
    ghost |= (hsv[..., 2] > 225) & (hsv[..., 1] < 60)
    ghost |= (hsv[..., 2] > 170) & (hsv[..., 1] < 40)   # faint grey ghost outlines
    skin = ((hsv[..., 0] < 22) | (hsv[..., 0] > 165)) & (hsv[..., 1] > 28)   # pinkish skin tones are never ghosts
    ghost &= ~skin
    o[ghost] = 255
    vw.write(o)
vw.release()
subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-i',src,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','copy',out],check=True)
os.remove(tmp); print('ok', out)
