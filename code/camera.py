from objects import Vec2i


class Camera:
    def __init__(self, target=None):
        self.position = Vec2i(0, 0)
        self.mode = "follow"
        self.target = target