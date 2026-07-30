import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geometry as geo
import toolpath as tp
import config as cfg

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
os.makedirs(OUTPUT_DIR, exist_ok=True)

STOCK_W, STOCK_H = geo.OUTPUT_STOCK_WIDTH, geo.STOCK_HEIGHT
SHIFT_X = geo.center_shift_x(STOCK_W)


def plot_stock_outline(ax):
    ax.plot([0, STOCK_W, STOCK_W, 0, 0], [0, 0, STOCK_H, STOCK_H, 0],
            color='black', linewidth=1.5, label='stock (18x12.5in)')
    ax.plot(0, 0, 'r+', markersize=14, markeredgewidth=2)
    ax.annotate('machine (0,0)\ntrue bottom-left corner', (0, 0),
                xytext=(15, 15), textcoords='offset points', color='red', fontsize=9)


fig, axes = plt.subplots(1, 4, figsize=(27, 8))

# --- eye whites pocket ---
ax = axes[0]
plot_stock_outline(ax)
ew = geo.eye_whites(SHIFT_X)
for sp in tp._subpolys(ew):
    xs, ys = sp.exterior.xy
    ax.plot(xs, ys, 'b-', linewidth=1, label='artwork boundary')
rings = tp.pocket_rings(ew, cfg.TOOL_RADIUS, cfg.STEPOVER_FRACTION * cfg.TOOL_DIAMETER)
for ring in rings:
    xs, ys = zip(*ring)
    ax.plot(xs, ys, 'g-', linewidth=0.4)
ax.set_title(f"Eye whites pocket\n{len(rings)} rings, depth {cfg.EYE_WHITE_DEPTH}mm")
ax.set_aspect('equal')
ax.set_xlim(-10, STOCK_W + 10)
ax.set_ylim(-10, STOCK_H + 10)

# --- pupils pocket ---
ax = axes[1]
plot_stock_outline(ax)
pu = geo.pupils(SHIFT_X)
for sp in tp._subpolys(pu):
    xs, ys = sp.exterior.xy
    ax.plot(xs, ys, 'b-', linewidth=1)
rings = tp.pocket_rings(pu, cfg.TOOL_RADIUS, cfg.STEPOVER_FRACTION * cfg.TOOL_DIAMETER)
for ring in rings:
    xs, ys = zip(*ring)
    ax.plot(xs, ys, 'g-', linewidth=0.4)
ax.set_title(f"Pupils pocket\n{len(rings)} rings, depth {cfg.PUPIL_DEPTH}mm")
ax.set_aspect('equal')
ax.set_xlim(-10, STOCK_W + 10)
ax.set_ylim(-10, STOCK_H + 10)

# --- mouth profile with tabs ---
ax = axes[2]
plot_stock_outline(ax)
mo = geo.mouth(SHIFT_X)
xs, ys = mo.exterior.xy
ax.plot(xs, ys, 'b-', linewidth=1, label='artwork boundary')
coords = tp.offset_profile(mo, cfg.TOOL_RADIUS, side='inside')
windows, lengths, total = tp.tab_windows(coords, cfg.TAB_COUNT, cfg.TAB_WIDTH)
xs2, ys2 = zip(*coords)
ax.plot(xs2, ys2, 'g-', linewidth=1, label='cutter path (inside offset)')
for j, (x, y) in enumerate(coords):
    if tp.in_any_window(lengths[j], windows, total):
        ax.plot(x, y, 'ro', markersize=2)
ax.set_title(f"Mouth through-cut\n{cfg.TAB_COUNT} tabs (red), depth {cfg.MOUTH_DEPTH}mm")
ax.set_aspect('equal')
ax.set_xlim(-10, STOCK_W + 10)
ax.set_ylim(-10, STOCK_H + 10)

for ax in axes:
    ax.legend(loc='upper right', fontsize=7)
    ax.grid(True, alpha=0.3)

# --- round-over pass ---
ax = axes[3]
plot_stock_outline(ax)
ax.plot(xs, ys, 'b-', linewidth=1, label='mouth SVG path')
roundover = mo.buffer(2.0, join_style=1)
rxs, rys = roundover.exterior.xy
ax.plot(rxs, rys, 'm-', linewidth=1.2, label='round-over path (+2mm)')
ax.set_title("Round-over pass\n2mm outside mouth, depth 2.5mm")
ax.set_aspect('equal')
ax.set_xlim(-10, STOCK_W + 10)
ax.set_ylim(-15, STOCK_H + 10)
ax.legend(loc='upper right', fontsize=7)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "scrappy_toolpath_preview.png"), dpi=130)
print("saved preview")

# Print a few sanity numbers
print(f"\nStock: {STOCK_W:.2f} x {STOCK_H:.2f} mm")
mb = mo.bounds
print(f"Mouth bounds (machine mm): x[{mb[0]:.2f},{mb[2]:.2f}] y[{mb[1]:.2f},{mb[3]:.2f}]")
if mb[1] < 0:
    print(f"*** WARNING: mouth extends {-mb[1]:.2f}mm BELOW machine Y=0 "
          f"(past the bottom edge of the nominal 12.5in stock) ***")
