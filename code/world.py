from support import tile_center
from objects import Vec2i, Transform
from camera import Camera
from render_priority import RenderPriority


class World:
    def __init__(self, game, entity_manager):
        self.game = game
        self.entity_manager = entity_manager
        self.tick = 0

        # Component Setup
        self.tile = set()
        self.actor = set()
        self.object = set()
        self.goal = {}
        self.transform = {}
        self.movement_footprint = {}
        self.motion_state = {}
        self.sprite = {}
        self.click_box = {}
        self.skills = {}

        # Map Setup: 0=blocked, 1=free
        self.map = [
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
        ]
        self.load_map()

        # Actor Setup
        self.player = self.spawn_player()

        ## Camera
        self.world_camera = Camera()
        self.world_camera.center_on(self.transform[self.player].cpos)

        # Debug
        self.spawn_player(spawn_tile=Vec2i(1, 0))


    def spawn_player(self, spawn_tile=None):
        if spawn_tile is None:
            spawn_tile = Vec2i(0, 0)

        eid = self.entity_manager.create()

        self.actor.add(eid)
        self.transform[eid] = Transform(cpos=tile_center(spawn_tile), prev_cpos=tile_center(spawn_tile), elevation=0)
        self.movement_footprint[eid] = "plus5"
        self.motion_state[eid] = {
            "controller": None,
            "last_delta": Vec2i(0, 0)
        }
        self.sprite[eid] = {
            "image_metadata": self.game.asset_manager.image_metadata["player"],
            "depth_offset": 0,
            "priority": RenderPriority.ACTOR,
        }
        self.skills[eid] = {
            "LMB": "attack",
        }

        return eid


    def load_map(self):
        for y, row in enumerate(self.map):
            for x, tile_type in enumerate(row):
                if tile_type == 0:
                    image_metadata = self.game.asset_manager.image_metadata["block"]
                elif tile_type == 1:
                    image_metadata = self.game.asset_manager.image_metadata["water"]

                tile_location = Vec2i(x, y)
                eid = self.entity_manager.create()

                self.tile.add(eid)
                self.transform[eid] = Transform(cpos=tile_center(tile_location), prev_cpos=tile_center(tile_location), elevation=0)
                self.sprite[eid] = {
                    "image_metadata": image_metadata,
                    "depth_offset": - image_metadata["image"].get_height() // 2,
                    "priority": RenderPriority.FLOOR,
                }
