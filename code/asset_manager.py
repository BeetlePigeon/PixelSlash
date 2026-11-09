from pathlib import Path
from sprite_anchor import SpriteAnchor
import pygame


class AssetManager:
    def __init__(self):
        self.image_metadata = {}

        base_path = Path(__file__).resolve().parent
        self.graphics_path = base_path.parent / "sprites"


    def load_image(self, *path_parts):
        path = self.graphics_path.joinpath(*path_parts)
        return pygame.image.load(path).convert_alpha()


    def load(self):
        # Player Characters
        self.image_metadata["player"] = {
            "image": self.load_image("characters", "player.png"),
            "anchor": SpriteAnchor.HUMAN
        }

        # Tiles
        self.image_metadata["block"] = {
            "image": self.load_image("tiles", "block.png"),
            "anchor": SpriteAnchor.FLOOR_BLOCK
        }

        self.image_metadata["water"] = {
            "image": self.load_image("tiles", "water.png"),
            "anchor": SpriteAnchor.FLOOR_BLOCK
        }