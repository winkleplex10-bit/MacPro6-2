#!/bin/sh
# Render floorplan: usage tools/render.sh macpro62_lga1700.kicad_pcb floorplan
#   <name>.png       board only (notes legend is on User.1 and excluded)
#   <name>_notes.png board + legend
cd "$(dirname "$0")/.." || exit 1
L=Edge.Cuts,F.Cu,F.Fab,B.Fab,F.CrtYd,B.CrtYd,Dwgs.User,Cmts.User,Eco1.User,Eco2.User,F.SilkS
kicad-cli pcb export svg --layers $L --page-size-mode 2 --exclude-drawing-sheet -o "$2.svg" "$1" >/dev/null && rsvg-convert -b white -w 3000 "$2.svg" -o "$2.png" && \
kicad-cli pcb export svg --layers $L,User.1 --page-size-mode 2 --exclude-drawing-sheet -o "$2_notes.svg" "$1" >/dev/null && rsvg-convert -b white -w 3600 "$2_notes.svg" -o "$2_notes.png" && echo rendered "$2.png" "$2_notes.png"
python3 - "$2.png" <<'PY'
import sys
from PIL import Image, ImageOps
p = sys.argv[1]; im = Image.open(p).convert("RGB")
bb = ImageOps.invert(im).getbbox()
m = 20
im.crop((max(0, bb[0] - m), max(0, bb[1] - m), min(im.width, bb[2] + m), min(im.height, bb[3] + m))).save(p)
print("cropped", p, bb)
PY
