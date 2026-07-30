"""Parse eyebrows.svg into its OWN machine-space coordinate system --
independent of scrappy.svg's stock-corner origin, per the user's
explicit instruction. Origin here = lower-left corner of the combined
eyebrow artwork's own bounding box.
"""
import os
import re
from svgelements import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union

SVG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "svg", "scrappy-wood", "eyebrows.svg")

# layer1 group transform (translate) -- applies to both path8, path9
LAYER1_DX = -50.714471
LAYER1_DY = -16.572097

FLATTEN_SEGMENTS_PER_CURVE = 48


def _extract_d_strings():
    content = open(SVG_PATH).read()
    blocks = re.findall(r'<path\b[^>]*?/?>', content, flags=re.S)
    info = {}
    for blk in blocks:
        idm = re.search(r'id="([^"]+)"', blk)
        dm = re.search(r'\bd="([^"]+)"', blk)
        if idm and dm:
            info[idm.group(1)] = dm.group(1)
    return info


def _flatten_path_to_coords(d_string, dx=0.0, dy=0.0):
    p = Path(d_string)
    coords = []
    for seg in p.segments():
        cls = seg.__class__.__name__
        if cls == 'Close':
            continue
        elif cls in ('Move', 'Line'):
            pt = seg.end
            coords.append((pt[0] + dx, pt[1] + dy))
        else:
            n = FLATTEN_SEGMENTS_PER_CURVE
            for i in range(1, n + 1):
                t = i / n
                pt = seg.point(t)
                coords.append((pt[0] + dx, pt[1] + dy))
    return coords


def _raw_shapes_svg_space():
    """Both eyebrow polygons in raw SVG-canvas space (mm, y-down), with the
    layer1 transform applied."""
    d_strings = _extract_d_strings()
    shapes = []
    for pid in ('path8', 'path9'):
        coords = _flatten_path_to_coords(d_strings[pid], dx=LAYER1_DX, dy=LAYER1_DY)
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        shapes.append(poly)
    return shapes


def origin_svg_space():
    """(min_x, max_y) of the combined artwork bbox in SVG space -- this
    point becomes machine (0,0)."""
    combined = unary_union(_raw_shapes_svg_space())
    minx, miny, maxx, maxy = combined.bounds
    return minx, maxy, (minx, miny, maxx, maxy)


def eyebrows_machine():
    """Both eyebrow shapes as a list of two Polygons in MACHINE space
    (mm, y-up), origin at the artwork's own bbox lower-left corner."""
    ox, oy, bbox = origin_svg_space()
    shapes = []
    for poly in _raw_shapes_svg_space():
        coords = [(x - ox, oy - y) for (x, y) in poly.exterior.coords]
        shapes.append(Polygon(coords))
    return shapes, bbox


if __name__ == "__main__":
    shapes, bbox = eyebrows_machine()
    print(f"SVG-space combined bbox: {bbox}")
    print(f"Origin (SVG space, becomes machine 0,0): "
          f"({bbox[0]:.3f}, {bbox[3]:.3f})")
    for i, s in enumerate(shapes):
        b = s.bounds
        print(f"eyebrow {i}: area={s.area:.1f}mm^2 "
              f"bounds(machine mm)=({b[0]:.3f},{b[1]:.3f})-({b[2]:.3f},{b[3]:.3f}) "
              f"valid={s.is_valid}")
