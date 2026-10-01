# MacPro6,2

An open PCB redesign of the Mac Pro (Late 2013, "trashcan"). It keeps the enclosure, the triangular thermal core, the fan and the stock 450 W PSU, and replaces every board with new ones.

- `docs/`: the architecture spec (v0.2), the face module spec, the lineup research, the stock hardware reference and the service references
- `kicad/`: KiCad projects (the round base board/backplane, the CPU carrier fallback)
- `mechanical/`: board outlines (DXF), scan traces and 3D-print test parts

Status: early design. The CPU board is our own LGA1700 socket board with an Apple-style contact frame. The faces are an open module spec (GPU on Face P, storage on Face S).
