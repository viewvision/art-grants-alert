"""Natural integration of a flat cartoon cut-out onto a real photo background.
Steps: contact shadow (AO) under feet, soft cast shadow on the floor/wall following
the light, slight colour match to the scene, matching grain, light wrap on edges,
and optional flashlight glow on the target surface."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

def contact_shadow(size, feet, spread=1.0, alpha=150):
    sh = Image.new('L', size, 0); d = ImageDraw.Draw(sh)
    for (x0, x1, y) in feet:
        d.ellipse((x0 - 30*spread, y - 18*spread, x1 + 30*spread, y + 18*spread), fill=alpha)
    return sh.filter(ImageFilter.GaussianBlur(10 * spread))

def cast_shadow(char, pos, size, shear=-0.45, squash=0.35, alpha=90, blur=25):
    """flat shadow of the character lying on the floor, sheared away from the light."""
    a = char.split()[3]
    w, h = a.size
    nh = int(h * squash)
    a = a.resize((w, nh))
    a = a.transform((w + int(abs(shear) * nh), nh), Image.AFFINE,
                    (1, shear, (shear * nh if shear < 0 else 0), 0, 1, 0), Image.BILINEAR)
    sh = Image.new('L', size, 0)
    x, yb = pos
    sh.paste(a.point(lambda v: v * alpha // 255), (int(x - (abs(shear) * nh if shear < 0 else 0)), int(yb - nh)))
    return sh.filter(ImageFilter.GaussianBlur(blur))

def match_colour(char, bg, amount=0.10):
    """pull the flat colours slightly toward the scene's average tone (scene light colour)."""
    tone = np.array(bg.convert('RGB').resize((1, 1), Image.BOX)).reshape(3).astype(np.float32)
    rgb = np.array(char.convert('RGB')).astype(np.float32)
    lum = rgb.mean(2, keepdims=True) / 255.0
    mixed = rgb * (1 - amount) + (tone * (0.6 + 0.5 * lum)) * amount
    out = Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8)); out.putalpha(char.split()[3]); return out

def light_wrap(char, bg_crop, width=6, amount=0.35):
    a = char.split()[3]
    inner = a.filter(ImageFilter.MinFilter(width * 2 + 1))
    edge = ImageChops.subtract(a, inner).filter(ImageFilter.GaussianBlur(width))
    blurred = bg_crop.convert('RGB').filter(ImageFilter.GaussianBlur(width * 2))
    base = char.convert('RGB')
    mix = Image.composite(Image.blend(base, blurred, amount), base, edge)
    mix.putalpha(a); return mix

def grain(img, strength=7, seed=0):
    rng = np.random.default_rng(seed)
    arr = np.array(img).astype(np.int16)
    n = rng.normal(0, strength, arr.shape[:2])[..., None]
    arr[..., :3] = np.clip(arr[..., :3] + n, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def glow(size, center, r, colour=(255, 244, 210), alpha=110):
    g = Image.new('RGBA', size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    x, y = center; d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=colour + (alpha,))
    return g.filter(ImageFilter.GaussianBlur(r * 0.5))
