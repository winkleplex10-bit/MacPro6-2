# Stock I/O cover phone scan check (2026-10-02 ≈ 11:30 ET)

Input: `raw/Untitled scan.ply` (from Aidan's zip, 11:07 ET), **Gaussian-splat PLY** (3DGS: xyz, normals, SH degree 3, opacity, scale, rot),
156,788 splats, no mesh faces, metres, ≈ 10k background splats. Shows the back/inner face only.

Run: `/workspace/cadenv/bin/python scan_overlay.py` → `io_cover_scan_check.json`, `io_cover_scan_overlay.png`
(panels: true-colour splats, density + plate v2 overlay with scan opening centroids, height residual vs R 110, cross-section R 110 / 102 / 82).

| Check | Scan | Plate v2 | Verdict |
|---|---|---|---|
| Scale / registration | ×0.931, 2.85°, mirrored, **RMS 0.49 mm** (13 openings), AC check 0.86 | – | Good 2D layout after rescale |
| Affine | 0.934 / 0.917 (1.8 % anisotropy), RMS 0.46 | – | Mild phone-scan distortion |
| Outline width | ≈ 52.4 (51.5–53.0 at 50 % density; blur ≈ +0.5) | 51.9 | Agrees, kept |
| Outline centre X | 53.0–53.5 | 53.19 | Agrees |
| Length | ≈ 160.3 (ends −3.0 / 157.3, fuzzy; top on the table) | 163.1 (−4.48 / 158.62) | Ends unreliable, kept |
| Corner radius | consistent with ≈ 11.5 | 11.5 | Kept |
| Inner radius | **101.7** (bootstrap 99.7–103.7; Y bands 94.8 / 94.0 / 122.8 / 102.4; half-width 77–102) | 109.97 (D0) | Consistent, not tighter: D0 kept |
| Clips / ribs / bosses / pins / glue pocket / wall | not resolvable (height MAD 1.36, splat 0.76) | unchanged | Measure by caliper |

Intermediates (`*.npy`, `*.npz`, `reg.json`, `props.json`) and `raw/` stay on the box and are not zipped.
