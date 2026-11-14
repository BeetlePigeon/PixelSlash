from support import Vec2i, tile_from_cpos


footprints = {
    "single": {
        "center": Vec2i(0, 0),
        "wings": (),
    },

    "plus": {
        "center": Vec2i(0, 0),
        "wings": (
            Vec2i(1, 0),
            Vec2i(-1, 0),
            Vec2i(0, 1),
            Vec2i(0, -1),
        ),
    }
}

def get_footprint_tiles(pos: Vec2i, footprint: str) -> tuple[Vec2i, list[Vec2i]]:
    """
    Returns the center tile and list of wing tiles of the actor's footprint at position 'pos'.

    'pos': Actor's world position.
    'footprint': Actor's occupancy footprint. Is either 'single' or 'plus'.
    """
    center = tile_from_cpos(pos)
    tiles = footprints[footprint]

    wings = []

    for offset in tiles["wings"]:
        wings.append(center + offset)

    return center, wings


def remove_occupancy(world, tile: Vec2i, footprint: str) -> None:
    """
    Updates the dynamic occupancy map based on the given footprint being placed at 'tile'.
    The occupancy count for any tile cannot be less than 0.

    There is no need to check for negative count since that could only occur from incorrect bookkeeping (which should
    be fixed elsewhere.)
    """
    wing_offsets = footprints[footprint]["wings"]
    world.single_dynamic_blockers[tile] -= 1
    world.plus_dynamic_blockers[tile] -= 1
    for offset in wing_offsets:
        world.plus_dynamic_blockers[tile + offset] += 1


def add_occupancy(world, tile: Vec2i, footprint: str) -> None:
    """Updates the dynamic occupancy map based on the given footprint being placed at 'tile'."""
    wing_offsets = footprints[footprint]["wings"]
    world.single_dynamic_blockers[tile] += 1
    world.plus_dynamic_blockers[tile] += 1
    for offset in wing_offsets:
        world.plus_dynamic_blockers[tile + offset] += 1