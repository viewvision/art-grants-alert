import sys
from PIL import Image
bg_path, fg_path, out, scale, bottom = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
bg = Image.open(bg_path).convert("RGBA").resize((1080, 1920), Image.LANCZOS)
fg = Image.open(fg_path)
tw = int(1080 * scale)
fg = fg.resize((tw, int(fg.height * tw / fg.width)), Image.LANCZOS)
x = (1080 - tw) // 2
y = int(1920 * bottom) - fg.height
bg.alpha_composite(fg, (x, y))
bg.convert("RGB").save(out, quality=92)
