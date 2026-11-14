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


def chebyshev_distance(vec1: Vec2i, vec2: Vec2i) -> int:
    return max(abs(vec1.x - vec2.x), abs(vec1.y - vec2.y))


def tiles_traversed(a: Vec2i, b: Vec2i) -> list[Vec2i]:
    """
    Returns a list of tiles intersected by the line from a to b (not including the tile 'a' is in.)
    On exact corner crossings, there's a tiebreak: the Y-axis step takes precedence.
    """
    curr_pos = a
    positions = []
    d = b - a
    dx, dy = d.x, d.y

    sign_x = 1 if dx > 0 else -1
    sign_y = 1 if dy > 0 else -1

    delta_tx = WORLD_UNITS / abs(dx) if dx != 0 else math.inf
    delta_ty = WORLD_UNITS / abs(dy) if dy != 0 else math.inf
    x = (a.x // WORLD_UNITS) * WORLD_UNITS + (WORLD_UNITS if sign_x > 0 else 0)
    y = (a.y // WORLD_UNITS) * WORLD_UNITS + (WORLD_UNITS if sign_y > 0 else 0)
    t_next_x = (x - a.x) / dx if dx != 0 else math.inf
    t_next_y = (y - a.y) / dy if dy != 0 else math.inf
    while t_next_x < 1 or t_next_y < 1:
        if t_next_x < t_next_y:
            curr_pos += Vec2i(sign_x * WORLD_UNITS, 0)
            positions.append(curr_pos)
            t_next_x += delta_tx
        else:
            curr_pos += Vec2i(0, sign_y * WORLD_UNITS)
            positions.append(curr_pos)
            t_next_y += delta_ty

    return [tile_from_cpos(position) for position in positions]