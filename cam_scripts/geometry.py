"""Parse scrappy.svg paths into machine-space Shapely polygons.

Coordinate convention:
  - SVG space: mm, y-down, origin at top-left of the 457.07618 x 317.86168mm canvas
    (canvas already matches the physical 18x12.5in stock, per project notes).
  - Machine space: mm, y-up, origin at the TRUE bottom-left corner of the stock.
    machine_x = svg_x
    machine_y = STOCK_HEIGHT - svg_y
This is a single fixed global transform -- every operation generated from this
module shares exactly the same physical zero point, by construction.
"""
import re
from svgelements import Path
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.affinity import translate

SVG_PATH = "/mnt/user-data/uploads/scrappy.svg"

# Original artwork canvas -- used only to resolve the SVG's own y-down -> y-up
# flip. This is NOT the physical output stock size (see OUTPUT_STOCK_WIDTH).
CANVAS_WIDTH = 457.07618   # mm (18in nominal)
STOCK_HEIGHT = 317.86168   # mm (12.5in nominal) -- output stock height, unchanged

# New output stock: 400mm wide, Scrappy centered horizontally on it.
OUTPUT_STOCK_WIDTH = 400.0

# layer1 ("Whites Layer") group transform -- applies to path1, path2 only
LAYER1_DY = -29.301879

FLATTEN_SEGMENTS_PER_CURVE = 48  # curve flattening resolution


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


def _flatten_path_to_coords(d_string, dy=0.0):
    """Flatten an SVG path 'd' string to a list of (x, y) in final SVG-canvas
    coordinates (dy applied), y-down."""
    p = Path(d_string)
    coords = []
    for seg in p.segments():
        cls = seg.__class__.__name__
        if cls == 'Move':
            pt = seg.end
            coords.append((pt[0], pt[1] + dy))
        elif cls == 'Close':
            pass
        elif cls in ('Line',):
            pt = seg.end
            coords.append((pt[0], pt[1] + dy))
        else:
            # Curve (CubicBezier, QuadraticBezier, Arc, etc.) -- sample finely
            n = FLATTEN_SEGMENTS_PER_CURVE
            for i in range(1, n + 1):
                t = i / n
                pt = seg.point(t)
                coords.append((pt[0], pt[1] + dy))
    return coords


def _svg_coords_to_machine(coords):
    return [(x, STOCK_HEIGHT - y) for (x, y) in coords]


def load_shape(path_id, dy=0.0):
    """Returns a Shapely Polygon in MACHINE coordinates (mm, y-up, origin at
    true stock bottom-left corner)."""
    d_strings = _extract_d_strings()
    d = d_strings[path_id]
    coords = _flatten_path_to_coords(d, dy=dy)
    machine_coords = _svg_coords_to_machine(coords)
    poly = Polygon(machine_coords)
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly


def _raw_eye_whites():
    left = load_shape('path1', dy=LAYER1_DY)
    right = load_shape('path2', dy=LAYER1_DY)
    return unary_union([left, right])


def _raw_pupils():
    left = load_shape('path3', dy=0.0)
    right = load_shape('path5', dy=0.0)
    return unary_union([left, right])


def _raw_mouth():
    return load_shape('path6', dy=0.0)


def center_shift_x(new_width=OUTPUT_STOCK_WIDTH):
    """X shift to center the combined artwork (all 5 shapes) on a stock of
    `new_width` mm, computed from the original canvas-space geometry."""
    combined = unary_union([_raw_eye_whites(), _raw_pupils(), _raw_mouth()])
    minx, _, maxx, _ = combined.bounds
    center_x = (minx + maxx) / 2
    return new_width / 2 - center_x


def eye_whites(shift_x=None):
    shift_x = center_shift_x() if shift_x is None else shift_x
    return translate(_raw_eye_whites(), xoff=shift_x, yoff=0)


def pupils(shift_x=None):
    shift_x = center_shift_x() if shift_x is None else shift_x
    return translate(_raw_pupils(), xoff=shift_x, yoff=0)


def mouth(shift_x=None):
    shift_x = center_shift_x() if shift_x is None else shift_x
    return translate(_raw_mouth(), xoff=shift_x, yoff=0)


if __name__ == "__main__":
    ew = eye_whites()
    pu = pupils()
    mo = mouth()
    for name, geom in [("eye-whites", ew), ("pupils", pu), ("mouth", mo)]:
        b = geom.bounds
        print(f"{name}: type={geom.geom_type} area={geom.area:.1f}mm^2 "
              f"bounds(machine mm, y-up)=({b[0]:.3f},{b[1]:.3f})-({b[2]:.3f},{b[3]:.3f}) "
              f"valid={geom.is_valid}")
