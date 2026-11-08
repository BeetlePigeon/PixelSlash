from support import tile_center
from objects import Vec2i, Transform
from camera import Camera


class World:
    def __init__(self, game, entity_manager):
        self.game = game
        self.entity_manager = entity_manager
        self.tick = 0

        ## Camera
        self.world_camera = Camera(self)

        # Area Setup: 0=free, 1=blocked
        self.map = [
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # Component Setup
        self.actor = set()
        self.object = set()
        self.goal = {}
        self.transform = {}
        self.movement_footprint = {}
        self.motion_state = {}
        self.sprite = {}
        self.skills = {}

        # Actor Setup
        self.player = self.spawn_player(Vec2i(0, 0))


    def spawn_player(self, spawn_tile):
        eid = self.entity_manager.create()

        self.actor.add(eid)
        self.transform[eid] = Transform(cpos=tile_center(spawn_tile), prev_cpos=tile_center(spawn_tile))
        self.movement_footprint[eid] = "plus5"
        self.motion_state[eid] = {
            "controller": None,
            "last_delta": Vec2i(0, 0)
        }
        self.sprite[eid] = {
            "image": self.game.asset_manager.images["player"],
            "anchor": "bottom_center",
            "z": 0,
        }
        self.skills[eid] = {
            "LMB": "attack",
        }

        return eid