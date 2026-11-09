from objects import Vec2i


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

# Both width and height of one isometric tile in pixels.
TILE_PIXELS = 32

# WORLD_UNITS is the number of canonical world units per tile.
# Tile coordinates are coarse grid positions.
# World units are fine-grained positions inside that grid.
# Example:
#     tile (0, 1) spans x from 0 to 1023 and y from 1024 to 2047.
WORLD_UNITS = 1024

# Internal render resolution.
# The game draws to this fixed-size surface first, then game.display scales
# that surface to the actual window/fullscreen size.
INTERNAL_WIDTH = 640
INTERNAL_HEIGHT = 480
INTERNAL_RES = Vec2i(INTERNAL_WIDTH, INTERNAL_HEIGHT)

# Safe y-position for recreating a windowed display after fullscreen/borderless.
# Prevents the OS title bar from being placed above the monitor edge.
WINDOW_TITLEBAR_SAFE_Y = 48