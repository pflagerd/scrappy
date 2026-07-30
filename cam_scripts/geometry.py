"""Parse scrappy-centered-on-4030-stock.svg paths into machine-space Shapely polygons.

That SVG is a pre-baked derivative of scrappy.svg: every group/path transform
is already resolved into the raw path data, and the combined eye-whites +
pupils + mouth artwork is already shifted to be centered on its 400x300mm
stock canvas (see the comment at the top of the SVG itself, and regenerate it
from scrappy.svg if the artwork or stock size changes). So this module only
needs the fixed SVG-to-machine coordinate flip -- no transform or centering
math here.

Coordinate convention:
  - SVG space: mm, y-down, origin at top-left of the 400 x 300mm canvas.
  - Machine space: mm, y-up, origin at the TRUE bottom-left corner of the stock.
    machine_x = svg_x
    machine_y = STOCK_HEIGHT - svg_y
"""
import os
import re
from svgelements import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union

SVG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "svg", "scrappy-wood", "scrappy-centered-on-4030-stock.svg")

STOCK_HEIGHT = 300.0         # mm -- actual physical output stock height
OUTPUT_STOCK_WIDTH = 400.0   # mm -- actual physical output stock width

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


def _flatten_path_to_coords(d_string):
    """Flatten an SVG path 'd' string to a list of (x, y) in SVG-canvas
    coordinates, y-down."""
    p = Path(d_string)
    coords = []
    for seg in p.segments():
        cls = seg.__class__.__name__
        if cls == 'Close':
            pass
        elif cls in ('Move', 'Line'):
            pt = seg.end
            coords.append((pt[0], pt[1]))
        else:
            # Curve (CubicBezier, QuadraticBezier, Arc, etc.) -- sample finely
            n = FLATTEN_SEGMENTS_PER_CURVE
            for i in range(1, n + 1):
                t = i / n
                pt = seg.point(t)
                coords.append((pt[0], pt[1]))
    return coords


def _svg_coords_to_machine(coords):
    return [(x, STOCK_HEIGHT - y) for (x, y) in coords]


def load_shape(path_id):
    """Returns a Shapely Polygon in MACHINE coordinates (mm, y-up, origin at
    true stock bottom-left corner)."""
    d_strings = _extract_d_strings()
    d = d_strings[path_id]
    coords = _flatten_path_to_coords(d)
    machine_coords = _svg_coords_to_machine(coords)
    poly = Polygon(machine_coords)
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly


def whites():
    return unary_union([load_shape('left-white'), load_shape('right-white')])


def pupils():
    return unary_union([load_shape('left-pupil'), load_shape('right-pupil')])


def mouth():
    return load_shape('mouth')


if __name__ == "__main__":
    ew = whites()
    pu = pupils()
    mo = mouth()
    for name, geom in [("whites", ew), ("pupils", pu), ("mouth", mo)]:
        b = geom.bounds
        print(f"{name}: type={geom.geom_type} area={geom.area:.1f}mm^2 "
              f"bounds(machine mm, y-up)=({b[0]:.3f},{b[1]:.3f})-({b[2]:.3f},{b[3]:.3f}) "
              f"valid={geom.is_valid}")
