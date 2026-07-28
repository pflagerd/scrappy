import config as cfg


class GCodeWriter:
    def __init__(self, title):
        self.lines = []
        self.lines.append(f"( {title} )")
        self.lines.append("( Origin: true bottom-left corner of the 18x12.5in stock )")
        self.lines.append("( Zero the machine at that corner before running this file )")
        self.lines.append("G21 ( mm )")
        self.lines.append("G90 ( absolute )")
        self.lines.append(f"M3 S{cfg.SPINDLE_RPM} ( ignored if spindle speed is set manually )")
        self.lines.append(f"G0 Z{cfg.SAFE_Z:.3f}")
        self._last_xy = None

    def comment(self, text):
        self.lines.append(f"( {text} )")

    def rapid_to(self, x, y, z=None):
        if z is None:
            self.lines.append(f"G0 X{x:.4f} Y{y:.4f}")
        else:
            self.lines.append(f"G0 X{x:.4f} Y{y:.4f} Z{z:.4f}")
        self._last_xy = (x, y)

    def safe_retract(self):
        self.lines.append(f"G0 Z{cfg.SAFE_Z:.3f}")

    def plunge_to(self, z):
        self.lines.append(f"G1 Z{z:.4f} F{cfg.FEED_PLUNGE:.0f}")

    def cut_to(self, x, y, z=None):
        if z is None:
            self.lines.append(f"G1 X{x:.4f} Y{y:.4f} F{cfg.FEED_XY:.0f}")
        else:
            self.lines.append(f"G1 X{x:.4f} Y{y:.4f} Z{z:.4f} F{cfg.FEED_XY:.0f}")
        self._last_xy = (x, y)

    def footer(self):
        self.lines.append(f"G0 Z{cfg.SAFE_Z:.3f}")
        self.lines.append("M5")
        self.lines.append("M2")

    def save(self, path):
        with open(path, "w") as f:
            f.write("\n".join(self.lines) + "\n")
