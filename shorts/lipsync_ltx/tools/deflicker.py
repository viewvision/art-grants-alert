"""Remove AI 'boiling' from flat 2D character videos.
usage: deflicker.py in.mp4 ref.png out.mp4 [k=10] [fps_div=1]
 - palette quantization to colors of the reference image (flat colors)
 - temporal majority filter on palette labels (5-frame window)
 - small spatial median to kill specks, slight AA blur
"""
import sys, subprocess, numpy as np, cv2
src, ref, out = sys.argv[1:4]
K = int(sys.argv[4]) if len(sys.argv) > 4 else 10
div = int(sys.argv[5]) if len(sys.argv) > 5 else 1
r = cv2.imread(ref)
lab_r = cv2.cvtColor(r, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
lab_r = lab_r[np.random.default_rng(0).choice(len(lab_r), 200000, replace=False)]
crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.5)
_, _, cent = cv2.kmeans(lab_r, K, None, crit, 3, cv2.KMEANS_PP_CENTERS)
# force pure white + pure black entries
cent = np.vstack([cent, cv2.cvtColor(np.uint8([[[255,255,255],[20,20,20]]]), cv2.COLOR_BGR2LAB).reshape(-1,3)]).astype(np.float32)
pal_bgr = cv2.cvtColor(cent.reshape(1,-1,3).astype(np.uint8), cv2.COLOR_LAB2BGR).reshape(-1,3)
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
labels = []
while True:
    ok, f = cap.read()
    if not ok: break
    L = cv2.cvtColor(cv2.bilateralFilter(f, 5, 20, 5), cv2.COLOR_BGR2LAB).astype(np.float32)
    d = ((L[:, :, None, :] - cent[None, None]) ** 2).sum(-1)
    labels.append(d.argmin(-1).astype(np.uint8))
lab = np.stack(labels); T = len(lab); n = len(cent)
outl = np.empty_like(lab)
for t in range(T):
    w = lab[max(0, t-2):t+3]
    cnt = np.stack([(w == c).sum(0) for c in range(n)])
    m = cnt.argmax(0).astype(np.uint8)
    # keep current label when it is tied with the winner (preserve fast mouth motion)
    keep = cnt[lab[t], np.arange(lab.shape[1])[:, None], np.arange(lab.shape[2])] if False else None
    outl[t] = cv2.medianBlur(m, 3)
H, W = lab.shape[1:]
tmp = out + '.tmp.mp4'
vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (W, H))
last = None
for t in range(T):
    if t % div == 0:
        img = pal_bgr[outl[t]]
        last = cv2.GaussianBlur(img, (3, 3), 0.6)
    vw.write(last)
vw.release()
subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-i',src,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','copy',out], check=True)
import os; os.remove(tmp)
print('ok', out, T, 'frames, palette', n)
