# Internal render resolution.
# The game draws to this fixed-size surface first, then the display code scales
# that surface to the actual window/fullscreen size.
INTERNAL_WIDTH = 640
INTERNAL_HEIGHT = 480
INTERNAL_RES = (INTERNAL_WIDTH, INTERNAL_HEIGHT)

# Fixed simulation rate.
# SIM_TICKS_PER_SECOND is the number of simulation ticks that happen in each second of elapsed game time.
# SIM_DT is the fixed amount of simulation time advanced by one tick in seconds.
# Game logic advances in fixed-size ticks so movement, cooldowns, actions,
# status durations, and effect timings are stable regardless of render FPS.
SIM_TICKS_PER_SECOND = 60
SIM_DT = 1.0 / SIM_TICKS_PER_SECOND

# Maximum real frame time that can be fed into the fixed-step accumulator.
# This prevents a large pause/stutter from trying to simulate too many ticks
# at once when the game resumes.
MAX_FRAME_DT = 0.25

# TILE_UNITS is the number of canonical world units per tile.
# Tile coordinates are coarse grid positions.
# cpos coordinates are fine-grained positions inside that grid.
# Example:
#     tile (0, 0) spans cpos x/y from 0 to TILE_UNITS - 1.
TILE_UNITS = 4096

# Pixel width/height of one isometric tile image before camera zoom/display scale.
# This is render-space size, not world-space size.
TILE_DIMENSION = 32

# Safe y-position for recreating a windowed display after fullscreen/borderless.
# Prevents the OS title bar from being placed above the monitor edge.
WINDOW_TITLEBAR_SAFE_Y = 48

# Fixed-point scale used for camera zoom.
# 1024 means 1.0x zoom.
# 512 means 0.5x zoom.
# 2048 means 2.0x zoom.
ZOOM_FP_SCALE = 1024