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

def get_footprint_tiles(pos, footprint):
    center = tile_from_cpos(pos)
    tiles = footprints[footprint]

    wings = []

    for offset in tiles["wings"]:
        wings.append(center + offset)

    return center, wings


def remove_occupancy(world, actor, center, wings):
    world.center_occupancy[center].remove(actor)
    if not world.center_occupancy[center]:  # Don't leave behind empty sets.
        del world.center_occupancy[center]

    for wing in wings:
        world.wing_occupancy[wing].remove(actor)
        if not world.wing_occupancy[wing]:  # Don't leave behind empty sets.
            del world.wing_occupancy[wing]


def add_occupancy(world, actor, center, wings):
    world.center_occupancy.setdefault(center, set()).add(actor)
    for wing in wings:
        world.wing_occupancy.setdefault(wing, set()).add(actor)