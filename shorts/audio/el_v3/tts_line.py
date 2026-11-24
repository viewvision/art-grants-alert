# One-off line through ElevenLabs (key injected by the environment network secret)
import json, sys, urllib.request
voice, out, text = sys.argv[1], sys.argv[2], sys.argv[3]
settings = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {"stability": 0.5, "similarity_boost": 0.75, "speed": 1.0}
req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_192",
    data=json.dumps({"text": text, "model_id": "eleven_v3", "voice_settings": settings}).encode(),
    headers={"xi-api-key": "dummy", "Content-Type": "application/json"})
open(out, "wb").write(urllib.request.urlopen(req, timeout=300).read())
print(out)
