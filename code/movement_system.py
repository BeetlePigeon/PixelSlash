from support import norm, scale_vec_to_mag, tile_from_cpos, tile_center
from occupancy_utils import get_footprint_tiles, add_occupancy, remove_occupancy


def movement_system(world):
    for actor in world.walk_controller:
        controller = world.walk_controller[actor]
        budget = controller.speed
        nav = world.navigation[actor]
        waypoints = nav.waypoints

        while budget > 0 and waypoints:
            current_waypoint = waypoints[0]

            if norm(current_waypoint - world.transform[actor].cpos) == 0:
                waypoints.pop(0)
                continue

            result = get_first_viable_candidate(world, actor, budget)

            if result is None:
                record_block()
                on_block()
                break

            old_pos = world.transform[actor].cpos
            candidate, displacement = result
            new_pos = old_pos + displacement

            if tile_from_cpos(new_pos) != tile_from_cpos(old_pos):
                remove_occupancy(world, actor, old_pos)
                add_occupancy(world, actor, new_pos)

            world.transform[actor].cpos = new_pos
            budget -= norm(displacement)
            current_waypoint = waypoints[0]

            if norm(current_waypoint - new_pos) == 0:
                waypoints.pop(0)


def get_first_viable_candidate(world, actor, budget):
    controller = world.walk_controller[actor]
    pos = world.transform[actor].cpos
    candidates = controller.generate_candidates(pos, world.navigation[actor].waypoints[0])
    for candidate in candidates:
        direction = candidate - pos
        distance = norm(direction)

        if budget >= distance:
            displacement = direction
        else:
            displacement = scale_vec_to_mag(direction, budget)

        end_pos = pos + displacement
        if viable_candidate(world, actor, end_pos):
            return candidate, displacement

    return None


def viable_candidate(world, actor, end_pos):
    """Determines whether the actor's footprint can legally occupy end_pos.

    Current algorithm (uses endpoint-only collision validation):
     1) Check for center tile overlap with other actor centers.
     2) Check for center tile overlap with other actor wings.
     3) For each wing, check for overlap with other actor centers.
     4) Check for any footprint tiles overlapping with static obstructions.
     5) If at any point overlap is found return False, otherwise return True at the end.

    A possible future implementation using DDA Grid Traversal (checks intermediate
        footprint positions along the movement trajectory.):
     1) Obtain the list of tiles crossed by moving from current position to 'end_pos'.
     2) Check footprint placement validity at each of those tiles using above rules. If any are illegal, return
        False.
     3) Otherwise return True.

     Optional improvement: evaluate placement validity sequentially as each new tile is crossed and early
        return False if invalid placement found, instead of finding all tiles crossed and then checking."""

    footprint = world.footprint[actor]
    center, wings = get_footprint_tiles(end_pos, footprint)

    center_center_blockers = world.center_occupancy.get(center, ())
    for eid in center_center_blockers:
        if eid != actor:
            return False

    center_wing_blockers = world.wing_occupancy.get(center, ())
    for eid in center_wing_blockers:
        if eid != actor:
            return False

    for wing in wings:
        wing_center_blockers = world.center_occupancy.get(wing, ())
        for eid in wing_center_blockers:
            if eid != actor:
                return False

    for footprint_tile in [center, *wings]:
        if footprint_tile in world.static_occupancy:
            return False

    return True


def record_block():
    print("Actor was blocked - block recorded")


def on_block():
    print("Actor was blocked - no on block behavior")