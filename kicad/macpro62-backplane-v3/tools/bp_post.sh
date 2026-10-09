#!/bin/sh
# post-routing: bp_finish SRC -> DST, restore project rules, plane-net stitching (GND/3V3_SB), dangling clean-up, DRC summary
# usage: tools/bp_post.sh work/SRC.kicad_pcb DST.kicad_pcb   (run from the project folder)
set -e
SRC=$1; DST=$2; B=${DST%.kicad_pcb}
BPF_STAGE=A python3 tools/bp_finish.py "$SRC" "$DST" 2>&1 | grep -v "assert\|Debug" | tail -3
BPF_STAGE=B python3 tools/bp_finish.py "$DST" "$DST" 2>&1 | grep -v "assert\|Debug" | tail -5
cp work/pro_backup/backplane.kicad_pro "$B.kicad_pro"; cp work/pro_backup/backplane.kicad_dru "$B.kicad_dru"
python3 tools/bp_fix.py stitch "$DST" "$DST" 2>&1 | grep -v "assert\|swig" | tail -12
cp work/pro_backup/backplane.kicad_pro "$B.kicad_pro"; cp work/pro_backup/backplane.kicad_dru "$B.kicad_dru"
for i in 1 2 3 4 5 6; do python3 tools/bp_clean.py "$DST" 2>&1 | grep -v "assert\|swig\|Debug" > /tmp/bpclean.log || true; cat /tmp/bpclean.log; grep -q "dangling items 0\|removed 0" /tmp/bpclean.log && break; done
cp work/pro_backup/backplane.kicad_pro "$B.kicad_pro"; cp work/pro_backup/backplane.kicad_dru "$B.kicad_dru"
