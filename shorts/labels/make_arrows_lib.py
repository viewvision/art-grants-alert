"""Hand-drawn style white arrows (transparent PNG) for name labels."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = '/home/user/art-grants-alert/shorts/labels/'
S = 4  # supersample

def catmull(pts, n=40):
    pts = np.array(pts, float); P = np.vstack([pts[0], pts, pts[-1]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t + (-p0+3*p1-3*p2+p3)*t**3))
    out.append(P[-2]); return np.array(out)

def arrow(pts, size=(420, 420), width=11, head=46, color=(255, 255, 255), shadow=True):
    W, H = size[0]*S, size[1]*S
    c = catmull([(x*W, y*H) for x, y in pts])
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    w = width*S
    d.line([tuple(p) for p in c], fill=color, width=w, joint='curve')
    for p in (c[0], c[-1]):
        d.ellipse((p[0]-w/2, p[1]-w/2, p[0]+w/2, p[1]+w/2), fill=color)
    # open chevron head along end tangent
    tip = c[-1]; v = c[-1] - c[-6]; v /= np.linalg.norm(v)
    for ang in (150, -150):
        a = np.radians(ang); r = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        e = tip + r @ v * head*S
        d.line([tuple(tip), tuple(e)], fill=color, width=w)
        d.ellipse((e[0]-w/2, e[1]-w/2, e[0]+w/2, e[1]+w/2), fill=color)
    d.ellipse((tip[0]-w/2, tip[1]-w/2, tip[0]+w/2, tip[1]+w/2), fill=color)
    im = im.resize(size, Image.LANCZOS)
    if shadow:
        a = im.split()[3].point(lambda v: v*55//255)
        sh = Image.new('RGBA', size, (0, 0, 0, 0)); sh.putalpha(a); sh = sh.filter(ImageFilter.GaussianBlur(4))
        base = Image.new('RGBA', size); base.alpha_composite(sh, (0, 3)); base.alpha_composite(im); im = base
    return im

