from constants import WORLD_UNITS, TILE_PIXELS
from objects import Vec2i


def world_to_screen(world_pos: Vec2i, camera_pos: Vec2i) -> tuple[int, int]:
    """ Convert world coordinates to internal screen pixels.
    
    Uses a simple top-down view without isometric projection for now.
    The camera position represents the top-left of the visible area.
    """
    return (
        (world_pos.x - camera_pos.x) * TILE_PIXELS // WORLD_UNITS,
        (world_pos.y - camera_pos.y) * TILE_PIXELS // WORLD_UNITS,
    )