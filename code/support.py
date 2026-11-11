from objects import Vec2i
from constants import WORLD_UNITS
import math


def norm(vector: Vec2i) -> int:
    return round(math.sqrt(vector.x**2 + vector.y**2))


def tile_center(tile: Vec2i) -> Vec2i:
    return Vec2i(
        tile.x * WORLD_UNITS + WORLD_UNITS // 2,
        tile.y * WORLD_UNITS + WORLD_UNITS // 2,
    )


def tile_from_cpos(cpos: Vec2i) -> Vec2i:
    return Vec2i(
        cpos.x // WORLD_UNITS,
        cpos.y // WORLD_UNITS,
    )


def scale_vec_to_mag(vector: Vec2i, target_mag: int) -> Vec2i:
    length = norm(vector)

    if length == 0 or target_mag == 0:
        return Vec2i(0, 0)

    scaling_factor = target_mag / length

    return Vec2i(
        round(vector.x * scaling_factor),
        round(vector.y * scaling_factor),
    )