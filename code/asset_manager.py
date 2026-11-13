from pathlib import Path
from sprite_anchor import SpriteAnchor
import pygame


class AssetManager:
    def __init__(self):
        self.image_metadata = {}

        base_path = Path(__file__).resolve().parent.parent
        self.graphics_path = base_path / "sprites"


    def load_image(self, *path_parts):
        path = self.graphics_path.joinpath(*path_parts)
        return pygame.image.load(path).convert_alpha()


    def load(self):
        # Player
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

        # Objects
        self.image_metadata["chest"] = {
            "image": self.load_image("objects", "chest.png"),
            "anchor": SpriteAnchor.CHEST
        }

        # Debug
        self.image_metadata["debug_waypoint"] = {
            "image": self.load_image("debug", "highlighted_tile.png"),
            "anchor": SpriteAnchor.FLOOR_BLOCK
        }