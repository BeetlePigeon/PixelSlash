from objects import Vec2i
from constants import WORLD_UNITS


def tile_center(tile: Vec2i) -> Vec2i:
    return Vec2i(
        tile.x * WORLD_UNITS + WORLD_UNITS // 2,
        tile.y * WORLD_UNITS + WORLD_UNITS // 2,
    )