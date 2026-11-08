from objects import Vec2i
from constants import TILE_UNITS


def tile_center(tile: Vec2i) -> Vec2i:
    return Vec2i(
        tile.x * TILE_UNITS + TILE_UNITS // 2,
        tile.y * TILE_UNITS + TILE_UNITS // 2,
    )