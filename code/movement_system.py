from support import norm, scale_vec_to_mag, tile_from_cpos, tile_center, position_is_on_edge, get_tiles_traversed
from occupancy_utils import get_footprint_tiles, add_occupancy, remove_occupancy
from objects import Vec2i
from constants import WORLD_UNITS
from profiler import timed


@timed
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

        while budget > 0 and nav.goal_tile_center and not nav.blocked and (waypoints or not nav.goal_center_reached):
            old_pos = world.transform[actor].cpos
            if waypoints:
                next_waypoint = waypoints[0]
                if norm(next_waypoint - old_pos) == 0:
                    waypoints.pop(0)
                    continue
            else:
                next_waypoint = nav.goal_tile_center
                if norm(next_waypoint - old_pos) == 0:
                    nav.goal_center_reached = True
                    break
            direction = next_waypoint - old_pos
            distance = norm(direction)
            if budget >= distance:
                displacement = direction
            else:
                displacement = scale_vec_to_mag(direction, budget)
            new_pos = old_pos + displacement
            # If position lands exactly on boundary between 2 or more tiles, nudge it forward slightly so it belongs
            # explicitly to a single tile.
            new_pos = nudge_past_boundary(new_pos, direction)
            tiles_traversed = get_tiles_traversed(old_pos, new_pos)
            traversed_legal = all(legal_candidate(world, actor, tile_center(tile)) for tile in tiles_traversed)
            if traversed_legal:
                # Direct line path is unobstructed
                if tile_from_cpos(new_pos) != tile_from_cpos(old_pos):
                    remove_occupancy(world, tile_from_cpos(old_pos), footprint) # Remove footprint from old tile
                    add_occupancy(world, tile_from_cpos(new_pos), footprint) # Add footprint at new tile
                world.transform[actor].cpos = new_pos
                budget -= norm(displacement)
            else:
                # Direct line path is obstructed, mark actor blocked and recenter. Nav may start avoidance next tick.
                mark_walk_controller_blocked(world, actor)
                break


def nudge_past_boundary(pos: Vec2i, direction: Vec2i) -> Vec2i:
    x = pos.x
    y = pos.y
    if x % WORLD_UNITS == 0:
        if direction.x > 0:
            x += 1
        elif direction.x < 0:
            x -= 1
    if y % WORLD_UNITS == 0:
        if direction.y > 0:
            y += 1
        elif direction.y < 0:
            y -= 1
    return Vec2i(x, y)


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
    actor_pos = world.transform[actor].cpos
    footprint = world.footprint[actor]
    actor_tile, actor_wings = get_footprint_tiles(actor_pos, footprint)

    if tile == actor_tile:
        return True # Assumes current placement is already legal

    count = 0
    if tile in actor_wings:
        count -= 1

    if footprint == "single":
        count += world.single_dynamic_blockers[tile]
        count += 1 if tile in world.single_static_blockers else 0

    elif footprint == "plus":
        count += world.plus_dynamic_blockers[tile]
        count += 1 if tile in world.plus_static_blockers else 0

    return count == 0


def mark_walk_controller_blocked(world, actor):
    """
    Records a Navigator block and centers the actor so that blocked actors are grid aligned when stationary.
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


def get_first_legal_candidate(world, actor, budget):
    """
    NO LONGER USED. REMOVE ONCE MOVEMENT AND NAVIGATION IS STABLE.

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