from support import tile_center
from objects import Vec2i, Transform
from camera import Camera
from render_priority import RenderPriority


class World:
    """
    Container for the game world's entities, components, and map.

    Uses a lightweight entity-component architecture:
        - An entity is identified by a unique integer ID (eid).
        - Components store the data associated with an entity.
        - Systems read and modify components to implement game behavior.

    Components are stored in sets or dictionaries keyed by eid.
    A single entity may and almost always will belong to multiple component collections.

    World also owns the map, simulation tick counter, player entity ID, and camera.
    """
    def __init__(self, game, entity_manager):
        self.game = game
        self.entity_manager = entity_manager
        self.tick = 0

        # Component Setup
        """Each collection is indexed by eid.

        Sets are tag components: they indicate membership or classification.
        Dictionaries are data components: eid -> component data

        Entities only receive the components relevant to their behavior."""
        # Tag components
        self.tile = set()       # Entities representing map tiles.
        self.actor = set()      # Entities capable of acting/moving.
        self.object = set()     # World objects, distinct from actors/tiles.

        # Gameplay components
        self.goal = {}                  # Current actor objective.
        self.transform = {}             # World position and elevation.
        # transform[eid] -> Transform
        #
        # cpos: Current world position in longitudinal plane in world units.
        # prev_cpos: Position from the previous simulation state. Used
        #   for render interpolation. Gets updated at the start of each
        #   tick.
        # elevation: Height used to vertically offset the entity.
        #
        # cpos and prev_cpos are Vec2i objects.
        self.walk_speed = {}        # Base movement speed.
        # walk_speed[eid] -> int
        #
        # Speed represents number of world units moved per tick.
        self.skills = {}            # Skill slot bindings.
        # skills[eid] -> {
        #   0: "attack",    # Skill equipped to slot 1 (LMB for player)
        #   1: "block",     # Skill equipped to slot 2 (RMB for player)
        #   2: "dash",      # Skill equipped to slot 3 (which is spacebar for player)
        #   ...,            # And so on...
        # }

        # Presentation and interaction components
        self.sprite = {}        # Sprite asset and rendering properties.
        # sprite[eid] -> {
        #   "image_metadata": ...,  # Shared asset data: image + anchor.
        #   "depth_offset": ...,    # Screen-pixel adjustment to sorting Y.
        #   "priority": ...,        # RenderPriority; breaks depth ties.
        # }
        self.click_box = {}     # Rectangles used for detecting mouse cursor overlap.

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
        self.sprite[eid] = {
            "image_metadata": self.game.asset_manager.image_metadata["player"],
            "depth_offset": 0,
            "priority": RenderPriority.ACTOR,
        }
        self.walk_speed[eid] = 225
        self.skills[eid] = {
            0: "attack",
            1: "counter",
            2: "dash",
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
