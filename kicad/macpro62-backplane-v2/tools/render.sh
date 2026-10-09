#!/bin/bash
# render.sh board.kicad_pcb out.png layers [width]
kicad-cli pcb export svg --layers "$3" --mode-single --page-size-mode 2 --exclude-drawing-sheet -o /tmp/_r.svg "$1" >/dev/null 2>&1 && rsvg-convert -b white -w ${4:-2400} /tmp/_r.svg -o "$2"
