from support import norm, scale_vec_to_mag
from occupancy_utils import get_footprint_tiles, add_occupancy, remove_occupancy


def movement_system(world):
    for actor in world.walk_controller:
        controller = world.walk_controller[actor]
        budget = controller.speed
        nav = world.navigator[actor]
        waypoints = nav.waypoints
        transform = world.transform[actor]

        while budget > 0 and waypoints:
            current_waypoint = waypoints[0]

            if norm(current_waypoint - transform.cpos) == 0:
                waypoints.pop(0)
                continue

            result = get_first_viable_candidate(world, actor, budget)

            if result is None:
                record_block()
                on_block()
                break

            candidate, displacement = result

            old_center, old_wings = get_footprint_tiles(transform.cpos, world.footprint[actor])
            transform.cpos += displacement
            new_center, new_wings = get_footprint_tiles(transform.cpos, world.footprint[actor])

            if new_center != old_center:
                remove_occupancy(world, actor, old_center, old_wings)
                add_occupancy(world, actor, new_center, new_wings)

            budget -= norm(displacement)
            current_pos = transform.cpos
            current_waypoint = waypoints[0]

            if norm(current_waypoint - current_pos) == 0:
                waypoints.pop(0)


def get_first_viable_candidate(world, actor, budget):
    controller = world.walk_controller[actor]
    candidates = controller.get_candidates()
    pos = world.transform[actor].cpos
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