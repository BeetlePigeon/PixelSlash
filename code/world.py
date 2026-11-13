from support import tile_center
from objects import Vec2i, Transform
from camera import Camera
from render_priority import RenderPriority
from navigation import Navigator
from controllers import WalkController
from occupancy_utils import add_occupancy
from map import test_map


class World:
    """Container for the game world's entities, components, and map.

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
        self.object = set()     # World objects that can be interacted with, distinct from actors/tiles.

        self.center_occupancy = {}
        # center_occupancy[Vec2i(9, 2)] -> {1}           # Actors 1 has their center tile at tile (9, 2).
        self.wing_occupancy = {}
        # wing_occupancy[Vec2i(3, 4)] -> {1, 50, 201}       # Actors 1, 50, and 201 have a wing tile at tile (3, 4).
        self.static_occupancy = set()
        # static_occupancy = {Vec2i(1, 1), Vec2i(2, 2)}     # Tiles (1, 1) and (2, 2) are statically obstructed.
        #
        # All occupancy structures are sparse.

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
        self.footprint = {}         # The space occupying footprint of entity.
        self.navigation = {}
        self.walk_controller = {}   # What actors use to navigate to goal targets.
        # walk_controller[eid] = WalkController()
        #
        # Handles local steering towards current navigation waypoint.
        self.skills = {}            # Skill slot bindings.
        # skills[eid] -> {
        #   0: "attack",    # Skill equipped to slot 1 (LMB for player)
        #   1: "block",     # Skill equipped to slot 2 (RMB for player)
        #   2: "dash",      # Skill equipped to slot 3 (which is spacebar for player)
        #   ...,            # And so on...
        # }

        # Presentation and interaction components
        self.clickbox = {}                 # Rectangles used for detecting mouse cursor overlap.
        # clickbox[eid] -> {
        #   "size": Vec2i(50, 50), # Clickbox (width, height) in pixels.
        #   "offset": Vec2i(0, 10), # Offsets the clickbox center from the entity.
        self.object_interact_range = {}     # Used for objects: specifies maximum tile distance away to interact with.
        self.sprite = {}        # Sprite asset and rendering properties.
        # sprite[eid] -> {
        #   "image_metadata": ...,  # Shared asset data: image + anchor.
        #   "depth_offset": ...,    # Screen-pixel adjustment to sorting Y.
        #   "priority": ...,        # RenderPriority; breaks depth ties.
        # }

        # Map Setup
        self.map = test_map
        self.load_map()

        # Actor Setup
        self.player = self.spawn_player()

        ## Camera
        self.world_camera = Camera()
        self.world_camera.center_on(self.transform[self.player].cpos)

        # Debug
        self.debug_setup()


    def remove_entity(self, eid):
        print("Entity cleanup not implemented")


    def spawn_player(self, spawn_tile=None):
        if spawn_tile is None:
            spawn_tile = Vec2i(5, 5)

        eid = self.entity_manager.create()

        self.actor.add(eid)
        self.transform[eid] = Transform(cpos=tile_center(spawn_tile), prev_cpos=tile_center(spawn_tile), elevation=0)
        self.footprint[eid] = "plus"
        add_occupancy(self, eid, tile_center(spawn_tile))
        self.navigation[eid] = Navigator([])
        self.walk_controller[eid] = WalkController()
        self.skills[eid] = {
            0: "attack",
        }
        self.sprite[eid] = {
            "image_metadata": self.game.asset_manager.image_metadata["player"],
            "depth_offset": 0,
            "priority": RenderPriority.ACTOR,
        }

        return eid


    def load_map(self):
        for y, row in enumerate(self.map):
            for x, tile_type in enumerate(row):
                tile_location = Vec2i(x, y)
                if tile_type == 0:
                    image_metadata = self.game.asset_manager.image_metadata["block"]
                    self.static_occupancy.add(tile_location)
                elif tile_type == 1:
                    image_metadata = self.game.asset_manager.image_metadata["water"]

                eid = self.entity_manager.create()

                self.tile.add(eid)
                self.transform[eid] = Transform(cpos=tile_center(tile_location), prev_cpos=tile_center(tile_location), elevation=0)
                self.sprite[eid] = {
                    "image_metadata": image_metadata,
                    "depth_offset": - image_metadata["image"].get_height() // 2, # Use the very top of the tile for depth sort.
                    "priority": RenderPriority.FLOOR,
                }


    def debug_setup(self):
        eid = self.entity_manager.create()
        tile = Vec2i(28, 18)
        self.object.add(eid)
        self.static_occupancy.add(tile)
        self.transform[eid] = Transform(cpos=tile_center(tile), prev_cpos=tile_center(tile), elevation=0)
        image_metadata = self.game.asset_manager.image_metadata["chest"]
        self.clickbox[eid] = {
            "size": Vec2i(50, 50),
            "offset": Vec2i(0, 0),
        }
        self.object_interact_range[eid] = 2
        self.sprite[eid] = {
            "image_metadata": image_metadata,
            "depth_offset": 0,
            "priority": RenderPriority.CHEST,
        }