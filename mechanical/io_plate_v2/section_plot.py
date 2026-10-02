"""Explanatory section at Y = 65.45 (USB-C row) and Y = 37.7 (USB-A): curved plate, flat lands, straight connectors."""
import math, json, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = 82.0; C = 53.19; SK = 1.2
zs = lambda x: -(R - math.sqrt(R * R - (x - C) ** 2))
fig, axs = plt.subplots(2, 1, figsize=(11, 7))
for ax, (title, lands, ports, pw, ph) in zip(axs, [("Section Y = 65.45 (USB-C C2 / C5 row)", [(42.6, 10.6), (63.9, 10.6)], [42.6, 63.9], 8.94, 6.5),
                                                 ("Section Y = 37.7 (USB-A pair)", [(43.3, 15.6), (64.05, 15.6)], [43.3, 64.05], 13.1, 7.0)]):
    xs = [27.24 + i * 0.1 for i in range(520)]
    ax.plot(xs, [zs(x) for x in xs], "k-", lw=1, label="stock-curve outer face (R 82, MEASURE M-IOT2)")
    ax.plot(xs, [zs(x) - SK for x in xs], "k--", lw=0.8, label="plate inner face (1.2 skin)")
    for cx, w in lands:
        zl = min(zs(cx - w / 2), zs(cx + w / 2))
        ax.fill_between([cx - w / 2, cx + w / 2], [zl - 1.0] * 2, [zl] * 2, color="#bbbbff", label="flat land + 1.0 boss (parallel to board)" if cx == lands[0][0] else None)
        ax.plot([cx - w / 2, cx + w / 2], [zl, zl], "b-", lw=2)
    for cx in ports:
        zl = min(zs(cx - (lands[0][1]) / 2), zs(cx + (lands[0][1]) / 2))
        top = zl if pw < 10 else zl - 1.2
        ax.add_patch(plt.Rectangle((cx - pw / 2, top - ph), pw, ph, fc="#cccccc", ec="k", label="straight receptacle (mouth/face)" if cx == ports[0] else None))
        u = cx - C; ang = math.degrees(math.asin(u / R))
        ax.annotate("stock shell normal %.1f deg" % ang, (cx, zs(cx)), (cx - 8, 2.2), fontsize=7, arrowprops=dict(arrowstyle="-", lw=0.5))
    ax.set_xlim(26, 81); ax.set_ylim(-11, 4); ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.set_title(title, fontsize=9)
    ax.set_xlabel("Xb (mm, back view)"); ax.set_ylabel("z (mm, 0 = crown of the outer face)")
axs[0].legend(fontsize=7, loc="lower center", ncol=2)
plt.tight_layout(); plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "io_plate_v2_A0_section.png"), dpi=140)
