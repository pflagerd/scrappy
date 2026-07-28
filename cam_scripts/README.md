# Scrappy CAM pipeline

Generates GRBL G-code directly from `scrappy.svg`, no CAM GUI involved.

## Setup
```bash
pip install -r requirements.txt --break-system-packages
```
Edit `SVG_PATH` at the top of `geometry.py` to point at your SVG file.

## Files
- `config.py`     -- all machining parameters (feeds, depths, stepover, tabs). Edit this first.
- `geometry.py`   -- parses the SVG, resolves transforms, converts to machine
                      space, handles centering on a given stock width.
- `toolpath.py`   -- pocket ring generation (concentric offsets) and profile
                      offset with tabs. Pure geometry, no G-code.
- `gcode.py`       -- minimal G-code writer (GRBL-flavored G0/G1/G21/G90).
- `main.py`        -- ties it together, writes the three .gcode files.
- `verify.py`      -- renders toolpath_preview.png so you can eyeball
                      everything against the stock outline before cutting.

## Run
```bash
python3 main.py      # writes scrappy_1_eye_whites.gcode, _2_pupils.gcode, _3_mouth.gcode
python3 verify.py     # writes scrappy_toolpath_preview.png
```

## To change something
- Different feed/plunge/stepover/stepdown/tab sizes -> edit `config.py`, rerun `main.py`.
- Different stock width / centering -> change `OUTPUT_STOCK_WIDTH` in `geometry.py`.
- New/different artwork -> point `SVG_PATH` at a new file; if it has group
  transforms like the original layer1 translate, add them in `geometry.py`
  the same way `LAYER1_DY` is handled.
