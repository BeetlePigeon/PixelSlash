from support import chebyshev_distance


def in_range_of_goal(current_tile, target_tile, completion_range):
    """Determines whether the actor is in range of its goal.
    'action_range' is the tile distance from the 'current_tile' to the 'target_tile'."""
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
    Returns the minimum tile distance the actor must be from the target to initiate the goal action.

    For 'walk' it's 0.
    For 'interact' it's 1.
    For 'use_skill' it's determined by the skill.
    """
    goal = world.goal[actor]
    mode = goal["mode"]
    nav = world.navigation[actor]

    if mode == "walk":
        completion_range = 0
    if mode == "interact":
        completion_range = 1
    if mode == "use_skill":
        raise ValueError(f"{mode} not implemented")

    return completion_range