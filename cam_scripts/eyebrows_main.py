import math
import eyebrows_geometry as ebg
import toolpath as tp
from gcode import GCodeWriter

# ---- Eyebrow-specific parameters (independent of Scrappy's config.py) ----
TOOL_DIAMETER = 1.5          # mm, plunge bit for the cutout
TOOL_RADIUS = TOOL_DIAMETER / 2

SAFE_Z = 5.0
FEED_XY = 600.0               # mm/min -- smaller bit, lighter cut than the 1/8in tool
FEED_PLUNGE = 250.0
SPINDLE_RPM = 12000

STEPDOWN = 1.0                # mm/pass -- conservative for a small 1.5mm bit
STOCK_THICKNESS = 12.7        # 1/2in, same material as the rest of Scrappy
THROUGH_EXTRA = 0.5
CUTOUT_DEPTH = STOCK_THICKNESS + THROUGH_EXTRA   # 13.2mm

ROUNDOVER_DEPTH = 6.0          # mm, single pass, per spec

TAB_COUNT_PER_EYEBROW = 3
TAB_WIDTH = 3.0
TAB_HEIGHT = 1.5


def build_roundover(outfile):
    """Round-over pass: traced along the ORIGINAL svg path of each eyebrow
    (that's where the physical edge of the material sits after the cutout
    removes the offset waste) -- single pass, straight to ROUNDOVER_DEPTH."""
    shapes, _ = ebg.eyebrows_machine()
    gc = GCodeWriter("Eyebrows - round-over pass (along SVG edge, 6mm deep)")
    gc.comment("Origin: lower-left corner of the eyebrow artwork's own bounding box")
    gc.comment("Independent coordinate system -- NOT shared with the rest of Scrappy")
    for i, shape in enumerate(shapes):
        coords = list(shape.exterior.coords)
        gc.comment(f"-- eyebrow {i+1}/2 --")
        x0, y0 = coords[0]
        gc.rapid_to(x0, y0, SAFE_Z)
        gc.plunge_to(-ROUNDOVER_DEPTH)
        for (x, y) in coords[1:]:
            gc.cut_to(x, y, -ROUNDOVER_DEPTH)
        gc.safe_retract()
    gc.footer()
    gc.save(outfile)
    return shapes


def build_cutout(outfile):
    """Cutout pass: offset OUTWARD from each eyebrow's svg path by the tool
    radius (so the kept piece matches the drawn shape), multi-pass through
    the material, with tabs holding each piece in place."""
    shapes, _ = ebg.eyebrows_machine()
    gc = GCodeWriter("Eyebrows - cutout (outside offset, through-cut with tabs)")
    gc.comment("Origin: lower-left corner of the eyebrow artwork's own bounding box")
    gc.comment("Independent coordinate system -- NOT shared with the rest of Scrappy")
    passes = max(1, math.ceil(CUTOUT_DEPTH / STEPDOWN))
    pass_depth = CUTOUT_DEPTH / passes
    tab_top_z = -(CUTOUT_DEPTH - TAB_HEIGHT)
    gc.comment(f"{passes} Z passes of {pass_depth:.4f}mm to {CUTOUT_DEPTH:.3f}mm total, "
               f"{TAB_COUNT_PER_EYEBROW} tabs/eyebrow")

    per_shape = []
    for shape in shapes:
        coords = tp.offset_profile(shape, TOOL_RADIUS, side='outside')
        windows, lengths, total = tp.tab_windows(coords, TAB_COUNT_PER_EYEBROW, TAB_WIDTH)
        per_shape.append((coords, windows, lengths, total))

    for i in range(1, passes + 1):
        z_target = -i * pass_depth
        gc.comment(f"-- pass {i}/{passes}, target Z={z_target:.4f} --")
        for si, (coords, windows, lengths, total) in enumerate(per_shape):
            def eff_z(s, windows=windows, total=total):
                if tp.in_any_window(s, windows, total):
                    return max(z_target, tab_top_z)
                return z_target
            gc.comment(f"eyebrow {si+1}/2")
            x0, y0 = coords[0]
            gc.rapid_to(x0, y0, SAFE_Z)
            gc.plunge_to(eff_z(lengths[0]))
            for j in range(1, len(coords)):
                x, y = coords[j]
                gc.cut_to(x, y, eff_z(lengths[j]))
            gc.safe_retract()
    gc.footer()
    gc.save(outfile)
    return per_shape


if __name__ == "__main__":
    import os
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    shapes = build_roundover(os.path.join(OUTPUT_DIR, "eyebrows_1_roundover.gcode"))
    print("round-over written")
    per_shape = build_cutout(os.path.join(OUTPUT_DIR, "eyebrows_2_cutout.gcode"))
    print("cutout written")
    for i, (coords, windows, lengths, total) in enumerate(per_shape):
        print(f"eyebrow {i}: {len(coords)} pts, perimeter {total:.1f}mm, "
              f"{len(windows)} tabs")
