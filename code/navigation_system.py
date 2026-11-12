from support import tile_from_cpos
from goal_utils import in_range_of_goal, clear_goal


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
        completion_range = world.navigation[actor].completion_range

        in_range = in_range_of_goal(current_tile, target_tile, completion_range)

        if not in_range:
            if not nav.initial_route_planned:
                nav.initial_route_planned = True
                generate_waypoints(world, actor)
                can_enable_walk = world.walk_controller[actor].request_enable_controller()
                if can_enable_walk:
                    world.walk_controller[actor].enabled = True
            else:
                if nav.blocked is True:
                    result = handle_navigation_block(world, actor)
                    if result == "failure":
                        clear_goal(world, actor)

                elif target_pos_is_stale(world, actor):
                    generate_waypoints(world, actor)
                    can_enable_walk = world.walk_controller[actor].request_enable_controller()
                    if can_enable_walk:
                        world.walk_controller[actor].enabled = True


def generate_waypoints(world, actor):
    """Creates waypoints for the navigator."""
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]

    if mode == "walk":
        world.navigation[actor].waypoints = [target]
    else:
        raise ValueError(f"{mode} not implemented")


def handle_navigation_block(world, actor):
    """
    Decides whether to populate new waypoints or do nothing when the actor is blocked.
    Returns True if the

    Currently: discards goal when blocked.
    Future: blocked results in waypoint regeneration (up to 1 time) or doing nothing for some ticks to give movement
    candidates an opportunity to become legal.
    """
    return "failure"


def target_pos_is_stale(world, actor) -> bool:
    """Determines whether current final waypoint is in completion range of target's current position."""
    nav = world.navigation[actor]
    goal = nav.goal
    mode = goal["mode"]
    target = goal["target"]

    navigation_target_tile = tile_from_cpos(nav.waypoints[-1])
    actual_target_tile = tile_from_cpos(target) if mode == "walk" else tile_from_cpos(world.transform[goal.target].cpos)
    completion_range = nav.completion_range

    if not in_range_of_goal(navigation_target_tile, actual_target_tile, completion_range):
        return True

    return False