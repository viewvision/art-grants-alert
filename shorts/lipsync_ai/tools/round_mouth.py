"""Overlay round mouths (closed / small-o / large-o) on an AI action video.
usage: round_mouth.py video audio out.mp4 audio_offset_sec ref_frame_idx gx0 gy0 gx1 gy1 mx my mw mh
 g* = glasses box in ref frame (tracking template), m* = mouth center/size in ref frame
"""
import sys, subprocess, numpy as np, cv2
vid, aud, out = sys.argv[1:4]
off = float(sys.argv[4]); ref_i = int(sys.argv[5])
gx0, gy0, gx1, gy1, mx, my, mw, mh = map(int, sys.argv[6:14])
cap = cv2.VideoCapture(vid); fps = cap.get(cv2.CAP_PROP_FPS)
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
H, W = frames[0].shape[:2]
# audio envelope
pcm = subprocess.run(['ffmpeg','-v','error','-i',aud,'-ac','1','-ar','24000','-f','s16le','-'],capture_output=True).stdout
a = np.frombuffer(pcm, np.int16).astype(np.float32)/32768
hop = int(24000/12)  # 12 fps mouth
rms = np.array([np.sqrt(np.mean(a[i:i+hop]**2)) for i in range(0, len(a), hop)])
peak = np.percentile(rms[rms>0.01], 90) if (rms>0.01).any() else 1
lvl = np.where(rms < 0.12*peak, 0, np.where(rms < 0.55*peak, 1, 2))
# avoid single-step flicker: closed blips of 1 step inside speech -> small
for i in range(1, len(lvl)-1):
    if lvl[i]==0 and lvl[i-1]>0 and lvl[i+1]>0: lvl[i]=1
tmpl = cv2.cvtColor(frames[ref_i][gy0:gy1, gx0:gx1], cv2.COLOR_BGR2GRAY)
dx0, dy0 = mx-gx0, my-gy0
prev = (gx0, gy0)
outf = []
for i, f in enumerate(frames):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    sx0, sy0 = max(0, prev[0]-40), max(0, prev[1]-40)
    roi = g[sy0:sy0+(gy1-gy0)+80, sx0:sx0+(gx1-gx0)+80]
    r = cv2.matchTemplate(roi, tmpl, cv2.TM_CCOEFF_NORMED)
    _, mv, _, ml = cv2.minMaxLoc(r)
    if mv > 0.5: prev = (sx0+ml[0], sy0+ml[1])
    cx, cy = prev[0]+dx0, prev[1]+dy0
    t = i/fps - off
    k = int(t*12)
    L = lvl[k] if 0 <= k < len(lvl) else 0
    f = f.copy()
    if L > 0:
        # erase original mouth with local face color
        face = f[cy-mh-6:cy-mh-2, cx-4:cx+4].reshape(-1,3).mean(0)
        cv2.ellipse(f, (cx, cy), (mw//2+9, mh//2+9), 0, 0, 360, face.tolist(), -1, cv2.LINE_AA)
        rx, ry = (6, 7) if L == 1 else (8, 11)
        cv2.ellipse(f, (cx, cy+ry//3), (rx, ry), 0, 0, 360, (40, 30, 120), -1, cv2.LINE_AA)
        cv2.ellipse(f, (cx, cy+ry//3), (rx, ry), 0, 0, 360, (15, 15, 15), 3, cv2.LINE_AA)
    outf.append(f)
tmpv = out + '.tmp.mp4'
w = cv2.VideoWriter(tmpv, cv2.VideoWriter_fourcc(*'mp4v'), fps, (W, H))
for f in outf: w.write(f)
w.release()
ms = int(off*1000)
subprocess.run(['ffmpeg','-v','error','-y','-i',tmpv,'-i',aud,'-filter_complex',f'[1:a]adelay={ms}|{ms},apad[a]','-map','0:v','-map','[a]','-shortest','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',out], check=True)
import os; os.remove(tmpv)
print('levels', ''.join(map(str, lvl)))
