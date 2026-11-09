from enum import Enum
from objects import Vec2i


class SpriteAnchor(Enum):
    HUMAN = Vec2i(2, 3)
    FLOOR_BLOCK = Vec2i(5, 5)