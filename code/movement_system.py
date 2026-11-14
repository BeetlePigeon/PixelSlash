from support import norm, scale_vec_to_mag, tile_from_cpos, tile_center
from occupancy_utils import get_footprint_tiles, add_occupancy, remove_occupancy


def movement_system(world):
    """
    Sequentially processes and applies movements by controller type for entities with enabled controllers.
    If an entity has its motion controller(s) disabled, it gets centered on its current tile.
    """
    process_walk_controllers(world)
    center_non_moving_entities(world)


def process_walk_controllers(world):
    """
    Gets movement candidates for each actor with enabled walk_controller and applies the first
    legal one while budget remains. Records and handles block if no candidates are legal. Updates occupancy maps
    when applied movement transitions the actor into a new tile.
    """
    for actor in world.walk_controller:
        controller = world.walk_controller[actor]
        if controller.enabled is False:
            continue
        budget = controller.speed
        nav = world.navigation[actor]
        waypoints = nav.waypoints
        footprint = world.footprint[actor]

        while budget > 0 and waypoints:
            current_waypoint = waypoints[0]

            if norm(current_waypoint - world.transform[actor].cpos) == 0:
                waypoints.pop(0)
                continue

            result = get_first_legal_candidate(world, actor, budget)

            if result is None:
                mark_walk_controller_blocked(world, actor)
                break

            old_pos = world.transform[actor].cpos
            candidate, displacement = result
            new_pos = old_pos + displacement

            if world.game.debug_mode:
                world.game.state.debug.walk_candidate = candidate
            else:
                world.game.state.debug.walk_candidate = None

            if tile_from_cpos(new_pos) != tile_from_cpos(old_pos):
                remove_occupancy(world, tile_from_cpos(old_pos), footprint)
                add_occupancy(world, tile_from_cpos(new_pos), footprint)

            world.transform[actor].cpos = new_pos
            budget -= norm(displacement)
            current_waypoint = waypoints[0]

            if norm(current_waypoint - new_pos) == 0:
                waypoints.pop(0)


def get_first_legal_candidate(world, actor, budget):
    """
    Returns the first legal candidate and its resulting displacement from a list of
    candidates ordered by preference. Returns 'None' if none of the candidates are legal.
    """
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

        if legal_candidate(world, actor, end_pos) and legal_candidate(world, actor, candidate):
            return candidate, displacement

    return None


def legal_candidate(world, actor, end_pos):
    """
    Determines whether the actor can legally occupy 'end_pos'.

    A possible future implementation using DDA Grid Traversal (checks intermediate
        footprint positions along the movement trajectory.):
     1) Obtain the list of tiles crossed by moving from current position to 'end_pos'.
     2) Check footprint placement validity at each of those tiles using above rules. If any are illegal, return
        False.
     3) Otherwise return True.

     Optional improvement: evaluate placement validity sequentially as each new tile is crossed and early
        return False if invalid placement found, instead of finding all tiles crossed and then checking.
    """
    tile = tile_from_cpos(end_pos)
    if tile == tile_from_cpos(world.transform[actor].cpos):
        return True

    footprint = world.footprint[actor]
    if footprint == "single":
        result = tile not in world.single_static_blockers and world.single_dynamic_blockers[tile] == 0
        return result
    if footprint == "plus":
        static_block = tile in world.plus_static_blockers
        dynamic_block = world.plus_dynamic_blockers[tile] > 0
        result = not static_block and not dynamic_block
        print(f"static block: {static_block}, dynamic block: {dynamic_block}. Legal: {result}")
        return result


def mark_walk_controller_blocked(world, actor):
    """
    Records a Navigator block and centers the actor.
    """
    world.navigation[actor].blocked = True
    center_entity(world, actor)


def center_non_moving_entities(world):
    """
    Centers entities whose motion controllers are ALL disabled.
    Does NOT center entities who do not have any motion controller component.

    There is currently only one motion controller to check: walk_controller.
    When more controllers are added they need to be checked here.
    """
    for actor in world.walk_controller:
        if world.walk_controller[actor].enabled is False:
            center_entity(world, actor)


def center_entity(world, actor):
    world.transform[actor].cpos = tile_center(tile_from_cpos(world.transform[actor].cpos))