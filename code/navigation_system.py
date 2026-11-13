from objects import Vec2i
from support import norm, tile_from_cpos, tile_center, chebyshev_distance
from goal_utils import in_range_of_goal, get_goal_completion_range
import math


def navigation_system(world):
    """
    'navigation_system' creates waypoints for new goals and either regenerates waypoints or records Navigator failure
    in the case of a stale target or blocked navigation.

    Waypoints generated are based on the actor, target's current position, and completion range of the goal action.

    Navigator object contains the state of the route such as waypoints and blockage information,
     while navigation_system owns the navigation logic.
    """
    for actor, goal in list(world.goal.items()):
        nav = world.navigation[actor]
        in_range = in_range_of_goal(world, actor)

        if not in_range:
            if not nav.initial_route_planned:
                nav.initial_route_planned = True
                nav.waypoints = generate_waypoints(world, actor)
                world.walk_controller[actor].enabled = True

            else:
                if nav.blocked:
                    result = blocked_try_reroute(world, actor)
                    if result == "reroute_success":
                        nav.blocked = False
                        nav.waypoints = generate_block_reroute_waypoints(world, actor)
                        world.walk_controller[actor].enabled = True
                    elif result == "reroute_failure":
                        nav.failed = True
                        print(f"Navigation failure recorded for {world.goal[actor]["mode"]}")

                elif route_is_stale(world, actor):
                    nav.waypoints = generate_waypoints(world, actor)
                    world.walk_controller[actor].enabled = True


def generate_waypoints(world, actor):
    """Creates waypoints for the navigator."""
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]
    completion_range = get_goal_completion_range(world, actor)

    waypoints = []

    if mode == "walk":
        final_waypoint = target
    else:
        final_waypoint = tile_center(get_closest_in_range_tile(world, actor, target, completion_range))

    waypoints.append(final_waypoint)
    return waypoints


def get_closest_in_range_tile(world, actor, target, tile_range) -> Vec2i:
    actor_tile = tile_from_cpos(world.transform[actor].cpos)
    target_tile = tile_from_cpos(world.transform[target].cpos)

    closest = None
    best_tile_dist = math.inf
    best_world_dist = math.inf
    for y in range(-tile_range, tile_range + 1):
        for x in range(-tile_range, tile_range + 1):
            tile = Vec2i(target_tile.x + x, target_tile.y + y)
            if tile.x < 0 or tile.y < 0:
                continue    # Don't need to check out of bound tiles.
            diff = abs(tile - actor_tile)
            tile_dist = max(diff.x, diff.y)
            world_dist = norm(tile_center(tile) - world.transform[actor].cpos)
            if not closest:
                closest = tile
                best_tile_dist = tile_dist
                best_world_dist = world_dist
            if tile_dist < best_tile_dist:
                closest = tile
                best_tile_dist = tile_dist
                best_world_dist = world_dist
            elif tile_dist == best_tile_dist and world_dist < best_world_dist:
                # If two tiles are equal tile distance pick the one with the closer center.
                closest = tile
                best_tile_dist = tile_dist
                best_world_dist = world_dist

    return closest


def generate_block_reroute_waypoints(world, actor):
    waypoints = []
    return waypoints


def blocked_try_reroute(world, actor):
    """
    Determines whether navigation has failed or not when the actor is blocked.

    Returns 'reroute_success' when reroute is allowed.
    Returns 'reroute_failure' when reroute is not allowed.
    """
    return "reroute_failure"


def route_is_stale(world, actor) -> bool:
    """
    Determines if route is stale.
    If no waypoints, the route is stale since the actor still isn't in range.
    Otherwise, compares the final waypoint to the target's current position.
    """
    waypoints = world.navigation[actor].waypoints
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]

    if not waypoints:
        return True

    final_waypoint = waypoints[-1]

    if mode == "walk":
        return final_waypoint != target

    final_tile = tile_from_cpos(final_waypoint)
    target_tile = tile_from_cpos(world.transform[target].cpos)
    completion_range = get_goal_completion_range(world, actor)

    return chebyshev_distance(final_tile, target_tile) > completion_range