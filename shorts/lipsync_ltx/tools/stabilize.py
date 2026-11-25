"""Remove sub-pixel whole-frame jitter: align every frame to the first one
(phase correlation on the lower body, which should not move), then warp back.
usage: stabilize.py in.mp4 out.mp4"""
import sys, subprocess, os, numpy as np, cv2
src, out = sys.argv[1:3]
cap = cv2.VideoCapture(src); fps = cap.get(5); fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(f)
H, W = fr[0].shape[:2]
y0, y1 = int(H * 0.5), int(H * 0.97)   # legs/feet region: static anchor
win = cv2.createHanningWindow((W, y1 - y0), cv2.CV_32F)
ref = cv2.cvtColor(fr[0], cv2.COLOR_BGR2GRAY)[y0:y1].astype(np.float32)
tmp = out + '.v.mp4'; vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (W, H))
for f in fr:
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)[y0:y1].astype(np.float32)
    (dx, dy), _ = cv2.phaseCorrelate(ref, g, win)
    M = np.float32([[1, 0, -dx], [0, 1, -dy]])
    vw.write(cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE))
vw.release()
subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-i',src,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','10','-pix_fmt','yuv420p','-c:a','copy',out],check=True)
os.remove(tmp); print('ok', out)
