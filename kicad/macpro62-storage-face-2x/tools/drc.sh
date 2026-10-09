#!/bin/sh
# usage: tools/drc.sh BOARD.kicad_pcb [OUT.txt]  (copies the project .kicad_pro/.kicad_dru next to the board, runs kicad-cli DRC, summarizes)
B=$1; O=${2:-${B%.kicad_pcb}_drc.txt}; P=/workspace/kicad/macpro62-storage-face-2x/macpro62-storage-face-2x
case "$B" in *macpro62-storage-face-2x.kicad_pcb) ;; *) cp $P.kicad_pro ${B%.kicad_pcb}.kicad_pro; cp $P.kicad_dru ${B%.kicad_pcb}.kicad_dru; cp $(dirname $P)/fp-lib-table $(dirname $B)/ 2>/dev/null;; esac
kicad-cli pcb drc --schematic-parity --severity-error --severity-warning -o "$O" "$B" >/dev/null 2>&1
grep -E "^\[" "$O" | cut -d']' -f1 | sort | uniq -c
grep -E "Found [0-9]+ (unconnected|schematic|DRC)" "$O"
