"""Semicircle arrows, same style as make_arrows.py"""
import numpy as np, importlib.util
from PIL import Image
spec = importlib.util.spec_from_file_location('ma', '/home/user/art-grants-alert/shorts/labels/make_arrows_lib.py')
ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
OUT = '/home/user/art-grants-alert/shorts/labels/'
def arc(a0, a1, cx=0.5, cy=0.5, r=0.36, n=14):
    a = np.radians(np.linspace(a0, a1, n))
    return [(cx + r*np.cos(t), cy - r*np.sin(t)) for t in a]
specs = {
    'arc_upright': arc(265, 80, cx=0.56),   # C-shape: from bottom, around left, tip at top heading right
    'arc_upleft':  None,                    # mirror of upright
    'arc_up':      arc(185, 375, cy=0.40),  # bowl: down around bottom, tip heading up on right
    'arc_down':    arc(190, -10, cy=0.62),  # rainbow: over the top, tip heading down on right
}
imgs = {}
for k, pts in specs.items():
    if pts is None: continue
    imgs[k] = ma.arrow(pts)
imgs['arc_upleft'] = imgs['arc_upright'].transpose(Image.FLIP_LEFT_RIGHT)
for k, im in imgs.items(): im.save(OUT + f'arrow_{k}.png')
sheet = Image.new('RGBA', (4*220, 220), (70, 80, 90, 255))
for i, k in enumerate(['arc_upright', 'arc_upleft', 'arc_up', 'arc_down']):
    sheet.alpha_composite(imgs[k].resize((200, 200)), (i*220+10, 10))
sheet.convert('RGB').save(OUT + 'arrows_arc_sheet.jpg', quality=92)
print('ok')
