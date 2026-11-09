from objects import Vec2i


class Camera:
    """Camera position is the world coordinate shown at viewport center."""

    def __init__(self):
        self.position = Vec2i(0, 0)


    def center_on(self, world_pos: Vec2i):
        self.position = world_pos