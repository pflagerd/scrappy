# ---- Machine / tool ----
TOOL_DIAMETER = 3.175      # mm, 1/8in straight/plunge bit
TOOL_RADIUS = TOOL_DIAMETER / 2

SAFE_Z = 5.0                # mm above stock top surface, rapid clearance height
FEED_XY = 800.0              # mm/min, cutting feed
FEED_PLUNGE = 300.0          # mm/min, straight-plunge feed
SPINDLE_RPM = 12000          # only matters if your router is GRBL/relay-controlled;
                              # ignored in practice if speed is set by a manual dial

STEPDOWN = 1.5               # mm, max Z depth removed per pass (conservative for 1/8in in plywood)
STEPOVER_FRACTION = 0.40     # pocket clearing stepover, as a fraction of tool diameter

# ---- Depths (positive numbers, mm below stock top surface) ----
EYE_WHITE_DEPTH = 1.5875     # 1/16in
PUPIL_DEPTH = 0.79375        # 1/32in
STOCK_THICKNESS = 12.7       # 1/2in plywood
MOUTH_THROUGH_EXTRA = 0.5    # cut a bit past material thickness, into a sacrificial backer
MOUTH_DEPTH = STOCK_THICKNESS + MOUTH_THROUGH_EXTRA
