#!/bin/sh
# Render floorplan: usage tools/render.sh backplane.kicad_pcb floorplan
cd "$(dirname "$0")/.." && kicad-cli pcb export svg --layers Edge.Cuts,F.Fab,F.CrtYd,Dwgs.User,Cmts.User,F.SilkS --page-size-mode 2 --exclude-drawing-sheet -o "$2.svg" "$1" >/dev/null && rsvg-convert -b white -w 2400 "$2.svg" -o "$2.png" && echo rendered "$2.png"
