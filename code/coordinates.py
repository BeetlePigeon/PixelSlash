from constants import WORLD_UNITS, TILE_PIXELS
from objects import Vec2i


def world_to_screen(world_pos: Vec2i, camera_pos: Vec2i, viewport_size: Vec2i) -> Vec2i:
    """Convert world coordinates to internal screen pixels.

    Formula:
        Screen = Iso(World - Camera) + Screen Center

    World - Camera: where the object is relative to the camera in world units
    Iso(...): convert that relative position to isometric pixel units
    + Screen Center: shift the result so that the camera's position appears at the center of the screen

    Example:         (Assumes 640 x 480 viewport)
        Camera position: world (0, 0)
        Object at tile (1, 0): world (1024, 0)
        World - Camera = (1024, 0)
        Iso(...) = (16, 8)
        + Screen Center = (320, 240)
        = (336, 248)
            (Object appears 16 px right, 8 px down from center or one world tile along world +x-axis.)
    """
    relative = world_pos - camera_pos

    iso = Vec2i(
        (relative.x - relative.y) * TILE_PIXELS // (2 * WORLD_UNITS),
        (relative.x + relative.y) * TILE_PIXELS // (4 * WORLD_UNITS),
    )

    return iso + viewport_size // 2


def screen_to_world(screen_pos: Vec2i, camera_pos: Vec2i, viewport_size: Vec2i) -> Vec2i:
    """Convert internal screen pixels into a world position.

    Formula:
        World = InverseIso(Screen - Screen Center) + Camera

    Screen - Screen Center: where the object is relative to the viewport center in pixels
    InverseIso(...): convert the pixel distance to world coordinate displacement from camera center
    + Camera: shift relative position by camera position to get the real world position

    Example:         (Assumes 640 x 480 viewport)
        Camera position: world (0, 0)
        Object visually 16 px right, 8 px down of viewport center
        Screen - Screen Center = (336, 248) - (320, 240) = (16, 8)
        InverseIso(...) = (1024, 0)
        + Camera = (0, 0)
        = (1024, 0)
            (Object exists at world position (1024, 0) which is 1 tile along world +x-axis.)

    Example:         (Assumes 640 x 480 viewport)
        Camera position: world (4096, 4096)
        Object visually 20 px down of viewport center
        Screen - Screen Center = (320, 260) - (320, 240) = (0, 20)
        InverseIso(...) = (1280, 1280)
        + Camera = (4096, 4096)
        = (5376, 5376)
            (Object exists at world position (5376, 5376). Note moving cardinally on screen displaces x and y by equal magnitudes.)
    """
    relative = screen_pos - viewport_size // 2

    inverse_iso = Vec2i(
        (relative.x + 2 * relative.y) * WORLD_UNITS // TILE_PIXELS,
        (2 * relative.y - relative.x) * WORLD_UNITS // TILE_PIXELS,
    )

    return inverse_iso + camera_pos