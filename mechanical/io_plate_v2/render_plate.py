#!/usr/bin/env python3
"""Shaded STL renders of the IO plate (numpy + matplotlib, no trimesh): inner-face isometric + composite preview.
Usage: render_plate.py [tag]   (tag '' | _tilt12p5 | _eth2blank | _screwpt)"""
import sys, os, struct, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
HERE = os.path.dirname(os.path.abspath(__file__)); tag = sys.argv[1] if len(sys.argv) > 1 else ""
def load_stl(p):
    b = open(p, "rb").read(); n = struct.unpack("<I", b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("x", "<u2")]))
    return a["v"].reshape(n, 3, 3).astype(float)
T = load_stl(os.path.join(HERE, "io_plate_v2_A0%s.stl" % tag))
def view(ax, elev, azim, title):
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    e, a = np.radians(elev), np.radians(azim); cam = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    L = cam + np.array([0.3, 0.2, 0.4]); L /= np.linalg.norm(L)
    sh = 0.25 + 0.75 * np.clip(np.abs(N @ L), 0, 1)
    col = np.c_[sh * 0.80, sh * 0.80, sh * 0.84, np.ones(len(sh))]
    pc = Poly3DCollection(T, facecolors=col, edgecolors="none", linewidths=0); ax.add_collection3d(pc)
    c = T.reshape(-1, 3); mn, mx = c.min(0), c.max(0)
    ax.set_xlim(mn[0], mx[0]); ax.set_ylim(mn[1], mx[1]); ax.set_zlim(mn[2] - 2, mx[2] + 2)
    ax.view_init(elev=elev, azim=azim); ax.set_axis_off(); ax.set_title(title, fontsize=8); ax.set_box_aspect((mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2] + 4), zoom=1.25)
    ax.set_proj_type("ortho")
fig = plt.figure(figsize=(8, 10)); ax = fig.add_subplot(111, projection="3d")
view(ax, -55, -75, "IO plate v2 A0%s - INNER face (1x M1.6 centre post SCR_C1 PRIMARY (C2 removed) + 4x corner bosses, glue optional; button area: RAISED collar + key tab + 2 ear bosses (M1.4) + rib; corner screws -1.0 Y; W 52.7 R12.8; no clips/rim; 1.4 wall except port seats, bosses, button features)" % tag)
fig.tight_layout(); out_iso = os.path.join(HERE, "io_plate_v2_A0%s_iso_inner.png" % tag); fig.savefig(out_iso, dpi=120); plt.close(fig)
if tag == "":
    ims = [os.path.join(HERE, f) for f in ("flex_821-2222_check.png", "io_plate_v2_A0_outer.png", "io_plate_v2_A0_iso_inner.png", "io_plate_v2_A0_thickness.png", "io_plate_v2_A0_button_closeup.png")]
    fig, axs = plt.subplots(1, len(ims), figsize=(34, 13))
    for a_, f in zip(axs, ims): a_.imshow(plt.imread(f)); a_.set_axis_off(); a_.set_title(os.path.basename(f), fontsize=9)
    fig.suptitle("IO plate v2 A0 (rev 2026-10-04 ~15:30 ET): outline 52.7 x 163.1 R12.8, audio Ø5.3; power-button features (RAISED collar OD 15.0 / ID 12.4 x 0.8 + key tab, corner screws at Y 148.95 / 13.70, 2 ear BOSSES Ø3.0 x 1.0 for M1.4, locating rib) + 1x M1.6 centre screw SCR_C1 on a 0.97 post (PRIMARY; SCR_C2 removed) + 4x M1.6 corner screws (-1.0 Y); glue optional, HDMI +X / button -X, 1.4 wall elsewhere", fontsize=12)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "io_plate_v2_A0_preview.png"), dpi=90)
print("ok", out_iso)
