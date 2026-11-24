# Generate one ElevenLabs take per role (with timestamps) and split it into per-line MP3s
import base64, json, subprocess, sys, urllib.request, os

# "-" = key is injected by the environment network secret (header placeholder only)
KEY = "dummy" if sys.argv[1] == "-" else open(sys.argv[1]).read().strip()
role = sys.argv[2]
cfg = json.load(open(sys.argv[3]))[role]
SEP = "\n\n"
text = SEP.join(t for _, t in cfg["lines"])
body = {"text": text, "model_id": "eleven_v3", "voice_settings": cfg["settings"]}
req = urllib.request.Request(
    f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}/with-timestamps?output_format=mp3_44100_192",
    data=json.dumps(body).encode(), headers={"xi-api-key": KEY, "Content-Type": "application/json"})
try:
    res = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode()[:500]); sys.exit(1)
os.makedirs("src", exist_ok=True); os.makedirs("lines", exist_ok=True)
take = f"src/{role}_take.mp3"
open(take, "wb").write(base64.b64decode(res["audio_base64"]))
al = res["alignment"]
chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
assert "".join(chars) == text, "alignment text mismatch"

# char ranges of each line, then cut halfway into the gaps between lines
spans, pos = [], 0
for _, t in cfg["lines"]:
    spans.append((st[pos], en[pos + len(t) - 1])); pos += len(t) + len(SEP)
total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", take], capture_output=True, text=True).stdout)
for i, ((name, t), (s, e)) in enumerate(zip(cfg["lines"], spans)):
    a = max(0.0, s - 0.08) if i == 0 else (spans[i - 1][1] + s) / 2
    b = total if i == len(spans) - 1 else (e + spans[i + 1][0]) / 2
    b = min(b, e + 0.35)
    d = b - a
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", take,
                    "-af", f"afade=t=in:d=0.02,afade=t=out:st={max(d - 0.05, 0):.3f}:d=0.05,loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "44100", "-b:a", "192k", f"lines/{name}.mp3"], check=True)
    print(f"{name:18s} {d:5.2f}s  {t}")
