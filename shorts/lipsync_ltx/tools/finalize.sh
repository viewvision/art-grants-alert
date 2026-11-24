#!/bin/bash
# finalize.sh in_3x4.mp4 out_1080.mp4 : deflicker + 1080x1920 (3:4 clip placed at bottom, white top)
set -e
T=$(mktemp -d)
python3 "$(dirname "$0")/clean.py" "$1" "$T/c.mp4" 1
ffmpeg -v error -y -i "$T/c.mp4" -vf "scale=1080:1440:flags=lanczos,pad=1080:1920:0:480:white,setsar=1" -r 24 -c:v libx264 -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k "$2"
rm -rf "$T"
