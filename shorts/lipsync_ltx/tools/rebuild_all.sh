#!/bin/bash
cd "$(dirname "$0")/.."
A=../characters/architect_ref.png; C=../characters/client_ref.png
run(){ tools/finalize.sh "$1" "final/$2_1080.mp4" "$3" > /dev/null && echo "done $2"; }
run c1_architect_01_34.mp4 c1_architect_01 $A
run ../lipsync_ai/c1_client_ltx_v2_clean.mp4 c1_client_01 $C
run r02a_s2.mp4 c2_client_02a $C
run r02b_c2.mp4 c2_client_02b $C
run c2_architect_02_34.mp4 c2_architect_02 $A
run c3a03_s3.mp4 c3_architect_03 $A
run c3a04_s2.mp4 c3_architect_04 $A
run c3c03_s4.mp4 c3_client_03 $C
run c4a05_s1.mp4 c4_architect_05 $A
run c5c04_fear2_trim.mp4 c5_client_04_fear $C
run c5c04_s1.mp4 c5_client_04 $C
run c5a06_s2.mp4 c5_architect_06 $A
run c6a07_s2.mp4 c6_architect_07 $A
run c6c05_s2.mp4 c6_client_05 $C
echo ALLDONE
