from support import tile_from_cpos, chebyshev_distance


def in_range_of_goal(world, actor):
    """
    Determines whether the actor is in range of its goal.
    For goal mode 'walk' this means being at the target position.
    For other modes this means being within tile range.
    """
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]

    if mode == "walk":
        return world.transform[actor].cpos == target
    else:
        current_tile = tile_from_cpos(world.transform[actor].cpos)
        target_tile = tile_from_cpos(world.transform[target].cpos)
        completion_range = get_goal_completion_range(world, actor)
        if chebyshev_distance(current_tile, target_tile) <= completion_range:
            return True
        else:
            return False


def clear_goal(world, actor):
    """Removes a goal, resets the navigator, and disables walk_controller."""
    del world.goal[actor]
    world.navigation[actor].reset()
    world.walk_controller[actor].enabled = False


def get_goal_completion_range(world, actor) -> int:
    """
    Returns the maximum tile distance the actor can be from the target to initiate the goal action.

    For 'walk' it's 0.
    For 'interact' it's 1.
    For 'use_skill' it's determined by the skill.
    """
    goal = world.goal[actor]
    mode = goal["mode"]

    if mode == "walk":
        completion_range = 0
    if mode == "interact":
        completion_range = 1
    if mode == "use_skill":
        raise ValueError(f"{mode} not implemented")

    return completion_range