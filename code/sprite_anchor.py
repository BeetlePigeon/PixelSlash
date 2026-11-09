from enum import Enum
from objects import Vec2i


class SpriteAnchor(Enum):
    HUMAN = Vec2i(-26, -75)
    FLOOR_BLOCK = Vec2i(-16, -10)