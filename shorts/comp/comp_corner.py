"""④ 모서리 점검: insp4_corner.png 를 insp4_corner.jpg 위에 합성."""
import sys; sys.path.insert(0, 'comp')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from integrate import contact_shadow, cast_shadow, match_colour, light_wrap, grain, glow

bg = Image.open('bg/inspect/insp4_corner.jpg').convert('RGB')
ch = Image.open('characters/inspect/insp4_corner.png').convert('RGBA')
H = 1450; s = H / ch.height
ch = ch.resize((round(ch.width * s), H), Image.LANCZOS)
x0, feet_y = 850, 2630; y0 = feet_y - H
tip = (x0 + round(70 * s), y0 + round(30 * s))
gap = (760, 850)

out = bg.convert('RGBA')
# 손전등 빛줄기(아주 옅게) + 모서리 틈 글로우
beam = Image.new('L', bg.size, 0); d = ImageDraw.Draw(beam)
d.polygon([tip, (gap[0] - 150, gap[1] - 30), (gap[0] + 120, gap[1] + 60)], fill=95)
beam = beam.filter(ImageFilter.GaussianBlur(40))
out = Image.composite(Image.new('RGBA', bg.size, (255, 245, 215, 255)), out, beam)
out = Image.alpha_composite(out, glow(bg.size, gap, 240, alpha=165))
out = Image.alpha_composite(out, glow(bg.size, gap, 90, alpha=170))
# 바닥 그림자
w = ch.width
cs = cast_shadow(ch, (x0 + 40, feet_y + 10), bg.size, shear=0.55, squash=0.22, alpha=70, blur=30)
ct = contact_shadow(bg.size, [(x0 + int(w * 0.18), x0 + int(w * 0.62), feet_y - 8)], spread=1.3, alpha=150)
for sh in (cs, ct):
    out = Image.composite(Image.new('RGBA', bg.size, (35, 33, 30, 255)), out, sh)
# 캐릭터
c = match_colour(ch, bg.crop((x0, y0, x0 + w, feet_y)), 0.10)
c = light_wrap(c, bg.crop((x0, y0, x0 + w, feet_y)), 5, 0.30)
out.alpha_composite(c, (x0, y0))
out = grain(out.convert('RGB'), 6)
out.save('characters/inspect/comp_corner.jpg', quality=93)
out.resize((768, 1376)).save(sys.argv[1] if len(sys.argv) > 1 else '/dev/null', 'JPEG')
