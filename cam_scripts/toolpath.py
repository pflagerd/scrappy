"""Toolpath generation: pocket clearing (concentric offsets) and profile
cuts (single inward offset).  Pure geometry -- no G-code here, just lists
of (x, y[, z]) points in machine space.
"""
import math
from shapely.geometry import Polygon, MultiPolygon


def _subpolys(geom):
    if geom.geom_type == 'MultiPolygon':
        return list(geom.geoms)
    return [geom]


def pocket_rings(geom, tool_radius, stepover, min_area=1.0):
    """Concentric offset rings clearing the interior of `geom`, from the
    boundary (offset = tool_radius) inward.  Returns a list of rings, each
    a list of (x, y) closed-loop points, in cutting order."""
    rings = []
    for sp in _subpolys(geom):
        offset = tool_radius
        while True:
            shrunk = sp.buffer(-offset, join_style=1)  # round joins
            if shrunk.is_empty or shrunk.area < min_area:
                break
            for p in _subpolys(shrunk):
                if p.exterior is not None and len(p.exterior.coords) >= 4:
                    rings.append(list(p.exterior.coords))
            offset += stepover
    return rings


def offset_profile(geom, tool_radius, side='inside'):
    """Single offset contour for a profile cut. side='inside' shrinks the
    polygon by tool_radius (cutter stays inside the drawn line -- what you
    want when cutting out an opening so the opening matches the drawing).
    Returns a single list of (x, y) closed-loop points."""
    d = -tool_radius if side == 'inside' else tool_radius
    offset_geom = geom.buffer(d, join_style=1)
    if offset_geom.geom_type == 'MultiPolygon':
        offset_geom = max(offset_geom.geoms, key=lambda p: p.area)
    return list(offset_geom.exterior.coords)


def perimeter_length(coords):
    total = 0.0
    for i in range(1, len(coords)):
        x0, y0 = coords[i - 1]
        x1, y1 = coords[i]
        total += math.hypot(x1 - x0, y1 - y0)
    return total

