from objects import Vec2i
from support import tile_from_cpos, chebyshev_distance
from skills import skill_data


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
    For 'interact' it's determined by the interactable object.
    For 'use_skill' it's determined by the skill.
    """
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]
    skill = goal["skill"]

    if mode == "walk":
        completion_range = 0
    if mode == "interact":
        completion_range = world.object_interact_range[target]
    if mode == "use_skill":
        completion_range = skill_data[skill]["completion_range"]

    return completion_range


def all_tiles_in_completion_range(world, actor) -> list[Vec2i]:
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]
    completion_range = get_goal_completion_range(world, actor)
    tiles = []
    if mode == "walk":
        tiles.append(tile_from_cpos(target))
    else:
        target_tile = tile_from_cpos(world.transform[target].cpos)
        for x in range(target_tile.x - completion_range, target_tile.x + completion_range + 1):
            for y in range(target_tile.y - completion_range, target_tile.y + completion_range + 1):
                if Vec2i(x, y) == target_tile:
                    continue
                tiles.append(Vec2i(x, y))
    return tiles