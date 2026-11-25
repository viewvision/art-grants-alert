"""Re-centre pupils inside the glasses lenses (front-facing frames).
usage: center_eyes.py in.mp4 out.mp4 start_frame
Finds the two lens interiors (yellow regions enclosed by the black frame) in the
head area, measures the pupil (dark blob inside each lens) and redraws it at the
lens centre with the same size.
"""
import sys, subprocess, os, numpy as np, cv2
src, out, start = sys.argv[1], sys.argv[2], int(sys.argv[3])
cap = cv2.VideoCapture(src); fps = cap.get(5); W = int(cap.get(3)); H = int(cap.get(4))
tmp = out + '.v.mp4'; vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (W, H))
i = 0; log = []
while True:
    ok, f = cap.read()
    if not ok: break
    if i >= start:
        y0, y1, x0, x1 = 0, int(H * 0.30), int(W * 0.25), int(W * 0.75)
        roi = f[y0:y1, x0:x1]
        g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        dark = (g < 90).astype(np.uint8)
        # lens interiors = non-dark holes enclosed by dark rings
        cnts, hier = cv2.findContours(dark, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        holes = []
        for k, c in enumerate(cnts):
            if hier[0][k][3] >= 0:  # inner contour (hole)
                a = cv2.contourArea(c); x, y, w, h = cv2.boundingRect(c)
                if 300 < a < 8000 and 0.6 < w / max(h, 1) < 1.8: holes.append((x, y, w, h, c))
        holes = sorted(holes, key=lambda t: -cv2.contourArea(t[4]))[:2]
        if len(holes) == 2:
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV); yel = np.median(roi[(hsv[..., 1] > 120) & (hsv[..., 2] > 150)].reshape(-1, 3), 0).astype(int).tolist()
            for (x, y, w, h, c) in holes:
                m = np.zeros(g.shape, np.uint8); cv2.drawContours(m, [c], -1, 255, -1)
                inner = cv2.erode(m, np.ones((5, 5), np.uint8))
                pup = (dark > 0) & (inner > 0)
                ys, xs = np.nonzero(pup)
                if len(xs) < 20: continue
                pw, ph = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
                cx, cy = x + w / 2, y + h / 2
                log.append(round(float(xs.mean() - cx), 1))
                roi[inner > 0] = yel
                cv2.ellipse(roi, (int(round(cx)), int(round(ys.mean()))), (pw // 2, ph // 2), 0, 0, 360, (20, 20, 20), -1, cv2.LINE_AA)
            f[y0:y1, x0:x1] = roi
    vw.write(f); i += 1
vw.release()
subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-i',src,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','12','-pix_fmt','yuv420p','-c:a','copy',out],check=True)
os.remove(tmp)
print('pupil x-offset before fix (px, + = right):', log[:6], '...', log[-6:])
