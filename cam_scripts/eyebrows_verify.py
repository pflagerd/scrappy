import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import eyebrows_geometry as ebg
import eyebrows_main as ebm
import toolpath as tp

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gcode")
os.makedirs(OUTPUT_DIR, exist_ok=True)

shapes, bbox = ebg.eyebrows_machine()

fig, axes = plt.subplots(1, 2, figsize=(14, 9))

# --- round-over ---
ax = axes[0]
for shape in shapes:
    xs, ys = shape.exterior.xy
    ax.plot(xs, ys, 'm-', linewidth=1.5, label='round-over path (= svg edge)')
ax.plot(0, 0, 'r+', markersize=14, markeredgewidth=2)
ax.annotate('(0,0)\nartwork bbox lower-left', (0, 0), xytext=(10, 10),
            textcoords='offset points', color='red', fontsize=9)
ax.set_title(f"Round-over pass\ndepth {ebm.ROUNDOVER_DEPTH}mm, along SVG edge")
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

# --- cutout ---
ax = axes[1]
for shape in shapes:
    xs, ys = shape.exterior.xy
    ax.plot(xs, ys, 'b-', linewidth=1, label='svg path')
for shape in shapes:
    coords = tp.offset_profile(shape, ebm.TOOL_RADIUS, side='outside')
    xs, ys = zip(*coords)
    ax.plot(xs, ys, 'g-', linewidth=1, label='cutter path (+0.75mm outside)')
ax.plot(0, 0, 'r+', markersize=14, markeredgewidth=2)
ax.annotate('(0,0)', (0, 0), xytext=(10, 10), textcoords='offset points',
            color='red', fontsize=9)
ax.set_title(f"Cutout pass\ndepth {ebm.CUTOUT_DEPTH}mm")
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

for ax in axes:
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=7)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "eyebrows_toolpath_preview.png"), dpi=130)
print("saved preview")
print(f"combined bbox (svg space): {bbox}")
