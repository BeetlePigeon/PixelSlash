from objects import Vec2i
from support import norm, tile_from_cpos, tile_center, chebyshev_distance
from goal_utils import in_range_of_goal, get_goal_completion_range, all_tiles_in_completion_range
import math
from a_star import single_a_star, multi_a_star
from profiler import timed

search_cooldown = 4  # The enforced number of ticks between A* searches.
stale_threshold = 200  # The number of ticks since an actor has requested a pathfind before the request is
# considered stale and discarded.


@timed
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

        if actor in world.pf_requests:
            tick = world.pf_requests[actor]
            if tick - world.tick >= stale_threshold:
                world.pf_requests.popitem(last=False)
                nav.failed = True
                continue

        if not nav.goal_center_reached or not in_range:
            if not nav.initial_route_planned:
                nav.initial_route_planned = True
                nav.goal_tile_center = generate_goal_tile_center(world, actor)
                world.walk_controller[actor].enabled = True

            else:
                if nav.blocked:
                    if actor not in world.pf_requests:
                        world.pf_requests[actor] = world.tick
                    waypoints = generate_block_reroute_waypoints(world, actor)
                    if waypoints and waypoints != "pending":
                        nav.waypoints = waypoints
                        nav.blocked = False
                        world.walk_controller[actor].enabled = True
                        new_goal_tile_center = waypoints[-1]
                        if new_goal_tile_center != nav.goal_tile_center:
                            nav.goal_tile_center = new_goal_tile_center
                            nav.goal_center_reached = False
                    elif waypoints == "pending":
                        continue
                    else:
                        nav.failed = True

                elif route_is_stale(world, actor):
                    nav.waypoints = []
                    new_goal_tile_center = generate_goal_tile_center(world, actor)
                    world.walk_controller[actor].enabled = True
                    if new_goal_tile_center != nav.goal_tile_center:
                        nav.goal_tile_center = new_goal_tile_center
                        nav.goal_center_reached = False


def generate_goal_tile_center(world, actor) -> Vec2i | None:
    """Returns the goal tile center for the actor's goal."""
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]
    completion_range = get_goal_completion_range(world, actor)

    goal_tile_center = None

    if mode == "walk":
        goal_tile_center = target
    else:   # mode == "interact" or mode == "use_skill"
        goal_tile = get_closest_in_range_tile(world, actor, target, completion_range)
        if goal_tile:
            goal_tile_center = tile_center(goal_tile)

    return goal_tile_center


def generate_block_reroute_waypoints(world, actor):
    """
    Builds a set of reroute waypoints using A*. A* may fail and in that case an empty list is returned.
    Waypoints are tile centers.

    Engagement waypoint generation uses Multi-goal A* which is expensive and so is throttled to reduce CPU strain.
    NPCs enter a queue and can search when first in line. The player's searches are always approved.

    Avoidance waypoint generation uses Single-goal A* in a small area with few expansions so doesn't require throttling
    or queueing.
    """
    start_tile = tile_from_cpos(world.transform[actor].cpos)
    goal = world.goal[actor]
    footprint = world.footprint[actor]

    if goal["mode"] == "walk":
        destination_tile = tile_from_cpos(goal["target"])
        return generate_avoidance_waypoints(world, actor, start_tile, destination_tile, footprint)

    central_tile = tile_from_cpos(world.transform[goal["target"]].cpos)
    buffer_range = 7    # Tuned value for engagement range game feel
    completion_range = get_goal_completion_range(world, actor)
    engagement_range = completion_range + buffer_range
    # Engagement range is a tuned value which determines the minimum tile distance actors must be from their target
    # before an A* search for a valid engagement tile can be generated.

    if chebyshev_distance(start_tile, central_tile) <= engagement_range:
        next_pf_actor = next(iter(world.pf_requests)) if world.pf_requests else None
        # The player skips pathfinding throttle and can always search.
        if actor == world.player or (actor == next_pf_actor and world.tick - world.last_search >= search_cooldown):
            world.pf_requests.popitem(last=False)
            world.last_search = world.tick
            waypoints = generate_engagement_waypoints(world, actor, start_tile, central_tile, footprint)
            return waypoints
        else:
            return "pending"
    else:
        destination_tile = tile_from_cpos(world.navigation[actor].goal_tile_center)
        waypoints = generate_avoidance_waypoints(world, actor, start_tile, destination_tile, footprint)







def generate_engagement_waypoints(world, actor, start_tile, target_tile, footprint):
    potential_goals = all_tiles_in_completion_range(world, actor)
    waypoints = multi_a_star(world, actor, start_tile, potential_goals, target_tile, footprint)
    return waypoints


def generate_avoidance_waypoints(world, actor, start_tile, target_tile, footprint):
    waypoints = single_a_star(world, actor, start_tile, target_tile, footprint)
    return waypoints


def route_is_stale(world, actor) -> bool:
    """
    Determines if route is stale.
    If no waypoints, the route is stale since the actor still isn't in range of the goal.
    Otherwise, the route is stale if the final waypoint is outside of goal completion range.
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
    else:   # mode == "interact" or mode == "use_skill"
        final_tile = tile_from_cpos(final_waypoint)
        target_tile = tile_from_cpos(world.transform[target].cpos)
        completion_range = get_goal_completion_range(world, actor)
        return chebyshev_distance(final_tile, target_tile) > completion_range


def get_closest_in_range_tile(world, actor, target, tile_range) -> Vec2i | None:
    """
    Finds the closest tile to the target that is in completion range of the goal.

    Does not check this closest tile for legality. Navigation handles rerouting to a valid location if this closest tile
    turns out to be blocked.
    """
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