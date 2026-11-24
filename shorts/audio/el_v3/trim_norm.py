# Trim leading/trailing silence by energy, then loudness-normalize
import subprocess, sys, numpy as np
src, dst = sys.argv[1], sys.argv[2]
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(float)
e = np.array([np.sqrt((x[i:i + 160] ** 2).mean()) for i in range(0, len(x) - 160, 160)])
db = 20 * np.log10(e + 1); on = np.where(db > db.max() - float(sys.argv[3] if len(sys.argv) > 3 else 40))[0]
s = max(0, on[0] * 0.01 - 0.06); t = on[-1] * 0.01 + 0.18
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{t - s:.3f}", "-i", src,
                "-af", f"afade=t=in:d=0.02,afade=t=out:st={max(t - s - 0.05, 0):.3f}:d=0.05,loudnorm=I=-16:TP=-1.5:LRA=11",
                "-ar", "44100", "-b:a", "192k", dst], check=True, timeout=60)
print(dst, round(t - s, 2))
