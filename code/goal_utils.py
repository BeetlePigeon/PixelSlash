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
    world.navigation[actor].clear_navigator(world, actor)
    world.walk_controller[actor].enabled = False