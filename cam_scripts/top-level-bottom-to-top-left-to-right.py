( Face leveling passes vertical bottom to top (x = 0 to 254mm, y = 0 to 185mm, tool is 1" (25.4mm) wide.)
( Origin: true bottom-left corner of the workpiece)
( Zero the machine at that corner, then jog to corner of workpiece before running this file )
G21 ( mm )
G90 ( absolute )
M3 S12000 ( turn motor on, ignored if spindle speed is set manually )
G0 Z5.000
G0 X0 Y0 Z5.0000 ( Go to origin if not already there)
G1 Z-0.2500 F100 ( Lower gantry )

G1 X0 Y185 F100

G0 Z5.000
M5
M2
G0 Z5.000
