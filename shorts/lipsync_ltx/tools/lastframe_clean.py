"""lastframe_clean.py in.mp4 out.png : last frame with background reset to pure white (keeps largest character blob)"""
import sys, subprocess, cv2, numpy as np
src, out = sys.argv[1:3]
tmp = out + '.raw.png'
subprocess.run(['ffmpeg','-v','error','-y','-sseof','-0.05','-i',src,'-frames:v','1','-update','1',tmp],check=True)
f = cv2.imread(tmp); g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
mask = cv2.morphologyEx((g < 200).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
cnts, _ = cv2.findContours((lab == big).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
m = np.zeros(g.shape, np.uint8); cv2.drawContours(m, cnts, -1, 255, -1); m = cv2.dilate(m, np.ones((5, 5), np.uint8))
o = np.full_like(f, 255); o[m > 0] = f[m > 0]; cv2.imwrite(out, o)
import os; os.remove(tmp)
