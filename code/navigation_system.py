from support import tile_from_cpos
from goal_utils import in_range_of_goal, get_goal_completion_range


def navigation_system(world):
    """
    'navigation_system' does nothing for goals that are in range, otherwise creates waypoints for new goals
    and either regenerates waypoints or discards goals in the case of a stale target or blocked navigation.

    Waypoints generated are based on the actor, target's current position, and completion range of the goal action.

    Navigator object contains the state of the route such as waypoints and blockage information,
     while navigation_system owns the navigation logic.
    """
    for actor, goal in list(world.goal.items()):
        nav = world.navigation[actor]
        goal = world.goal[actor]
        mode = goal["mode"]
        target = goal["target"]

        current_tile = tile_from_cpos(world.transform[actor].cpos)
        target_tile = tile_from_cpos(target) if mode == "walk" else tile_from_cpos(world.transform[target].cpos)
        completion_range = get_goal_completion_range(world, actor)

        in_range = in_range_of_goal(current_tile, target_tile, completion_range)

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

                    if result == "reroute_failure":
                        nav.failed = True

                elif target_pos_is_stale(world, actor):
                    nav.waypoints = generate_waypoints(world, actor)
                    world.walk_controller[actor].enabled = True


def generate_waypoints(world, actor):
    """Creates waypoints for the navigator."""
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]

    waypoints = []
    if mode == "walk":
        final_waypoint = target
    else:
        raise ValueError(f"{mode} not implemented")

    waypoints.append(final_waypoint)
    return waypoints


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


def target_pos_is_stale(world, actor) -> bool:
    """Determines whether current final waypoint is in completion range of target's current position."""
    nav = world.navigation[actor]
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]

    navigation_target_tile = tile_from_cpos(nav.waypoints[-1])
    actual_target_tile = tile_from_cpos(target) if mode == "walk" else tile_from_cpos(world.transform[target].cpos)
    completion_range = get_goal_completion_range(world, actor)

    if not in_range_of_goal(navigation_target_tile, actual_target_tile, completion_range):
        return True

    return False