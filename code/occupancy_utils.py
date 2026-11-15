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


def add_occupancy(world, tile: Vec2i, footprint: str) -> None:
    update_occupancy(world, tile, footprint, 1)


def remove_occupancy(world, tile: Vec2i, footprint: str) -> None:
    update_occupancy(world, tile, footprint, -1)


def update_occupancy(world, tile: Vec2i, footprint: str, delta: int) -> None:
    """
    Updates the dynamic occupancy maps based on the given footprint being placed at 'tile'.
    The occupancy count for any tile cannot be less than 0. If that happens there is bad logic upstream.

    'tile': The tile where the actor's footprint to be added or removed is centered.
    'footprint': Either "single" or "plus".
    'delta': Either 1 for adding occupancy or -1 for removing occupancy.
    """
    world.single_dynamic_blockers[tile] += delta
    world.plus_dynamic_blockers[tile] += delta

    if footprint == "single":
        wing_offsets = footprints["plus"]["wings"]
        for offset in wing_offsets:
            world.plus_dynamic_blockers[tile + offset] += delta # Plus cannot stand orthogonally adjacent to single

    elif footprint == "plus":
        wing_offsets = footprints["plus"]["wings"]
        for offset in wing_offsets:
            world.single_dynamic_blockers[tile + offset] += delta # Single can't stand orthogonally adjacent to plus
            world.plus_dynamic_blockers[tile + offset] += delta # Plus can't stand orthogonally adjacent to plus