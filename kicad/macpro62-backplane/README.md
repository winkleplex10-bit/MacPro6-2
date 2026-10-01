# MacPro6,2 backplane (BP) - KiCad 9 project, rev A floorplan

Topology: **HUB** (Aidan, 2026-10-01). The CPU board plugs into J1 (Amphenol Mini Cool Edge 224, ME1022410103011, vertical SMT) and the BP routes PCIe x16 to J9 (MCIO 124, Face P) and x4 to J10 (MCIO 124, Face S).
Spec: `/workspace/macpro62-architecture-spec-v0.2.md` (sections 3 and 4.9).

| File | What |
|---|---|
| `backplane.kicad_pcb` / `.kicad_pro` | HUB floorplan, 6 layers, JLC06161H-2116 stackup, placeholders only (not routed) |
| `floorplan.png` / `.svg` | Render of the hub floorplan |
| `drc_report.txt` | `kicad-cli pcb drc --severity-all`: 0 violations, 0 unconnected |
| `fitcheck_floorplan.txt` | r_max <= 58 mm and hole-distance >= 6 mm per footprint |
| `lane_length_estimate.txt` | Estimated BP PCIe lane lengths (J1 -> MCIO) |
| `docs/cpulink_224_pinout_draft.csv` | CPU-LINK 224 pin list draft (from `tools/cpulink_pinout.py`) |
| `backplane_direct.kicad_pcb` | Saved DIRECT variant (4L JLC04161H-7628, no PCIe on BP) |
| `variants/` | Direct fit check, DRC and render; archived all-MCIO hub fit check |
| `backplane.kicad_sch` + sheets | Block-diagram stubs (hierarchical labels only; ERC reports only dangling-label stubs) |
| `MP62_Placeholders.pretty/` | Placeholder footprints (outer dimensions from vendor drawings) |

Rebuild (from this folder):

```
python3 tools/make_placeholders.py
rm -f backplane.kicad_pcb backplane.kicad_pro backplane.kicad_prl
python3 tools/build_pcb.py          # VARIANT=direct for backplane_direct.kicad_pcb
python3 tools/postprocess.py        # VARIANT=direct for the 4L stackup
kicad-cli pcb drc --severity-all -o drc_report.txt backplane.kicad_pcb
tools/render.sh backplane.kicad_pcb floorplan
python3 tools/cpulink_pinout.py
python3 tools/build_sch.py
```
