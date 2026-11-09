from objects import Vec2i
from constants import WORLD_UNITS, TILE_PIXELS

class Camera:
    def __init__(self):
        """A top-down camera whose position is the viewport's top-left coordinate."""
        self.position = Vec2i(0, 0)


    def center_on(self, world_pos: Vec2i, viewport_size: Vec2i):
        """Position the camera so world_pos appears at the viewport center."""
        half_viewport = viewport_size * WORLD_UNITS // (2 * TILE_PIXELS)    # half viewport width and height in world units

        self.position = world_pos - half_viewport