from objects import Vec2i
from constants import WORLD_UNITS
import math


def tile_center(tile: Vec2i) -> Vec2i:
    return Vec2i(
        tile.x * WORLD_UNITS + WORLD_UNITS // 2,
        tile.y * WORLD_UNITS + WORLD_UNITS // 2,
    )


def scale_vec_to_mag(vector: Vec2i, target_mag: int) -> Vec2i:
    magnitude_squared = vector.x**2 + vector.y**2

    if magnitude_squared == 0 or target_mag == 0:
        return Vec2i(0, 0)

    current_mag = math.sqrt(vector.x**2 + vector.y**2)

    scaling_factor = target_mag / current_mag

    return Vec2i(
        round(vector.x * scaling_factor),
        round(vector.y * scaling_factor),
    )