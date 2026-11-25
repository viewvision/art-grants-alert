#!/bin/bash
# finalize.sh in.mp4 out_1080.mp4 ref.png : flatten colours / remove ghosts + fit into 1080x1920 (white)
set -e
T=$(mktemp -d)
python3 "$(dirname "$0")/flatten.py" "$1" "$3" "$T/c.mp4"
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$T/c.mp4")
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$T/c.mp4")
if [ $((W*4)) -eq $((H*3)) ]; then VF="scale=1080:1440:flags=lanczos,pad=1080:1920:0:480:white"; else VF="scale=-2:1920:flags=lanczos,pad=1080:1920:(ow-iw)/2:0:white"; fi
ffmpeg -v error -y -i "$T/c.mp4" -vf "$VF,setsar=1" -r 24 -c:v libx264 -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k "$2"
rm -rf "$T"
