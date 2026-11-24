"""Calm AI 'boiling' on flat 2D character clips.
usage: clean.py in.mp4 out.mp4 [hold=1]   (hold=2 -> 12fps look, each drawing held 2 frames)
 1) ffmpeg atadenoise (temporal) for fill noise / line shimmer
 2) background specks: near-white, low-saturation pixels -> pure white
"""
import sys, subprocess, numpy as np, cv2, os
src, out = sys.argv[1:3]; hold = int(sys.argv[3]) if len(sys.argv) > 3 else 1
tmp1 = out + '.dn.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-vf','atadenoise=0a=0.08:1a=0.08:2a=0.08:0b=0.15:1b=0.15:2b=0.15:s=7','-c:v','libx264','-crf','10','-an',tmp1],check=True)
cap = cv2.VideoCapture(tmp1); fps = cap.get(cv2.CAP_PROP_FPS)
W = int(cap.get(3)); H = int(cap.get(4))
tmp2 = out + '.w.mp4'
vw = cv2.VideoWriter(tmp2, cv2.VideoWriter_fourcc(*'mp4v'), fps, (W, H))
i = 0; last = None
while True:
    ok, f = cap.read()
    if not ok: break
    if i % hold == 0:
        mn = f.min(2); mx = f.max(2)
        bg = (mn > 222) & ((mx.astype(int) - mn) < 18)
        bg = cv2.morphologyEx(bg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool) | ((mn > 240))
        f[bg] = 255
        last = f
    vw.write(last); i += 1
vw.release()
subprocess.run(['ffmpeg','-v','error','-y','-i',tmp2,'-i',src,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','copy',out],check=True)
os.remove(tmp1); os.remove(tmp2); print('ok', out)
