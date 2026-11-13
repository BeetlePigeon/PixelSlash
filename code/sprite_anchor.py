from enum import Enum
from objects import Vec2i


class SpriteAnchor(Enum):
    HUMAN = Vec2i(-26, -75)     # Between feet
    FLOOR_BLOCK = Vec2i(-16, -10)       # Center of the block's top face
    CHEST = Vec2i(-16, -23)     # Middle area of the bottom of the chest