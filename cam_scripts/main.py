import math
import geometry as geo
import toolpath as tp
import config as cfg
from gcode import GCodeWriter


def build_pocket(title, geom, depth, outfile, stepdown=cfg.STEPDOWN):
    rings = tp.pocket_rings(geom, cfg.TOOL_RADIUS, cfg.STEPOVER_FRACTION * cfg.TOOL_DIAMETER)
    passes = max(1, math.ceil(depth / stepdown))
    pass_depth = depth / passes

    gc = GCodeWriter(title)
    gc.comment(f"Pocket clear: {len(rings)} ring(s), {passes} Z pass(es) of "
               f"{pass_depth:.4f}mm to total depth {depth:.4f}mm")
    for i in range(1, passes + 1):
        z = -i * pass_depth
        gc.comment(f"-- pass {i}/{passes}, Z={z:.4f} --")
        for ring in rings:
            x0, y0 = ring[0]
            gc.rapid_to(x0, y0, cfg.SAFE_Z)
            gc.plunge_to(z)
            for (x, y) in ring[1:]:
                gc.cut_to(x, y, z)
            gc.safe_retract()
    gc.footer()
    gc.save(outfile)
    return len(rings), passes


def build_profile(title, geom, depth, outfile, stepdown=cfg.STEPDOWN):
    coords = tp.offset_profile(geom, cfg.TOOL_RADIUS, side='inside')
    total = tp.perimeter_length(coords)
    passes = max(1, math.ceil(depth / stepdown))
    pass_depth = depth / passes

    gc = GCodeWriter(title)
    gc.comment(f"Inside profile, {passes} Z pass(es) of {pass_depth:.4f}mm "
               f"to total depth {depth:.4f}mm")

    for i in range(1, passes + 1):
        z = -i * pass_depth
        gc.comment(f"-- pass {i}/{passes}, Z={z:.4f} --")
        x0, y0 = coords[0]
        gc.rapid_to(x0, y0, cfg.SAFE_Z)
        gc.plunge_to(z)
        for (x, y) in coords[1:]:
            gc.cut_to(x, y, z)
        gc.safe_retract()
    gc.footer()
    gc.save(outfile)
    return len(coords), passes, total


if __name__ == "__main__":
    import os
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gcode")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ew = geo.whites()
    n_rings, n_passes = build_pocket(
        "Scrappy - whites pocket (centered, 400mm stock)", ew, cfg.EYE_WHITE_DEPTH,
        os.path.join(OUTPUT_DIR, "scrappy_1_whites.gcode"),
        stepdown=cfg.EYE_WHITE_DEPTH / 2)
    print(f"whites: {n_rings} rings, {n_passes} passes")

    pu = geo.pupils()
    n_rings, n_passes = build_pocket(
        "Scrappy - pupils pocket (centered, 400mm stock)", pu, cfg.PUPIL_DEPTH,
        os.path.join(OUTPUT_DIR, "scrappy_2_pupils.gcode"))
    print(f"pupils: {n_rings} rings, {n_passes} passes")

    mo = geo.mouth()
    n_pts, n_passes, total = build_profile(
        "Scrappy - mouth through-cut (centered, 400mm stock)", mo, cfg.MOUTH_DEPTH,
        os.path.join(OUTPUT_DIR, "scrappy_3_mouth.gcode"))
    print(f"mouth: {n_pts} pts, {n_passes} passes, perimeter={total:.1f}mm")

    mb = mo.bounds
    print(f"\nMouth bounds on new stock (mm): x[{mb[0]:.2f},{mb[2]:.2f}] y[{mb[1]:.2f},{mb[3]:.2f}]")
    if mb[0] < 0 or mb[2] > geo.OUTPUT_STOCK_WIDTH:
        print("*** WARNING: mouth toolpath exceeds the 400mm stock width ***")
    if mb[1] < 0:
        print(f"*** WARNING: mouth extends {-mb[1]:.2f}mm below machine Y=0 "
              f"(past the bottom edge of the stock) ***")

    # --- round-over pass: same trajectory as the mouth cutout, 1mm steps to 4.5mm deep ---
    n_pts, n_passes, total = build_profile(
        "Scrappy - mouth round-over pass (same trajectory as cutout, 1mm steps to 4.5mm deep)",
        mo, 4.5, os.path.join(OUTPUT_DIR, "scrappy_4_mouth_roundover.gcode"),
        stepdown=1.0)
    print(f"\nround-over: {n_pts} pts, {n_passes} passes, perimeter={total:.1f}mm")
