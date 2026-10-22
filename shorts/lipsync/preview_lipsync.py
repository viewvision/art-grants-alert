# Render a quick lip-sync test (cut 1) to check the mouth sprites against the real voice lines
import subprocess, numpy as np, os, shutil
from PIL import Image

W, H, FPS, MOUTH_FPS = 1080, 1920, 24, 12
F = 0.45                                   # scale of the 3x layers in frame
ORIG = {"client": (170, 100), "architect": (570, 30)}
FEET_SRC_Y = 615

def load(name):
    b = Image.open(f"{name}_body_nomouth.png")
    m = [Image.open(f"{name}_mouth_{k}_{l}.png") for k, l in enumerate(["closed", "small", "wide", "o"])]
    sz = (int(b.width * F), int(b.height * F))
    return b.resize(sz, Image.LANCZOS), [x.resize(sz, Image.LANCZOS) for x in m]

def levels(path, offset, total):
    """Mouth state per mouth-frame from the line's loudness (0 closed, 1 small, 2 wide)."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float)
    hop = 16000 // MOUTH_FPS
    rms = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x), hop)])
    db = 20 * np.log10(rms + 1)
    peak = db.max()
    st = np.where(db < peak - 22, 0, np.where(db < peak - 9, 1, 2))
    out = np.zeros(int(total * MOUTH_FPS) + 1, int)
    o = int(offset * MOUTH_FPS)
    out[o:o + len(st)] = st[: len(out) - o]
    return out

lines = [("architect", "../audio/el/lines/c1_architect_01.mp3", 0.3), ("client", "../audio/el/lines/c1_client_01.mp3", 3.75)]
total = 5.0
state = {"architect": np.zeros(int(total * MOUTH_FPS) + 1, int), "client": np.zeros(int(total * MOUTH_FPS) + 1, int)}
for who, p, off in lines:
    state[who] = np.maximum(state[who], levels(p, off, total))

bg = Image.open("../bg/A_ext_gpt_1_post.jpg").convert("RGBA").resize((W, H), Image.LANCZOS)
chars = {n: load(n) for n in ORIG}
oy = 1800 - FEET_SRC_Y * 3 * F
ox = (W - (900 - 170) * 3 * F) / 2
os.makedirs("frames", exist_ok=True)
for fi in range(int(total * FPS)):
    fr = bg.copy()
    mi = int(fi / FPS * MOUTH_FPS)
    for n, (body, mouths) in chars.items():
        pos = (int(ox + (ORIG[n][0] - 170) * 3 * F), int(oy + ORIG[n][1] * 3 * F))
        fr.alpha_composite(body, pos)
        fr.alpha_composite(mouths[state[n][mi]], pos)
    fr.convert("RGB").save(f"frames/{fi:04d}.jpg", quality=90)

subprocess.run(["ffmpeg", "-loglevel", "error", "-y",
                "-i", "../audio/el/lines/c1_architect_01.mp3", "-i", "../audio/el/lines/c1_client_01.mp3",
                "-filter_complex", "[0]adelay=300|300[a];[1]adelay=3750|3750[b];[a][b]amix=inputs=2:normalize=0,apad[aout]", "-map", "[aout]",
                "-t", str(total), "tmp_audio.wav"], check=True)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", "frames/%04d.jpg", "-i", "tmp_audio.wav",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-shortest", "lipsync_test_cut1.mp4"], check=True)
shutil.rmtree("frames"); os.remove("tmp_audio.wav")
print("ok")
