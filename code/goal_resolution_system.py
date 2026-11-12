from support import tile_center, tile_from_cpos
from goal_utils import in_range_of_goal, clear_goal, get_goal_completion_range


def set_goal(world, actor, target, mode, skill=None):
    """
    Sets the goal of the actor and gives the navigator the goal and its completion range.

    Goals span a period of time and describe what the actor is trying to accomplish in the future.
    An actor can only have one goal at a time.
    Goal does not produce waypoints. Navigation produces waypoints based on the active goal.

    actor: The entity whose goal is being assigned
    target: Is either a world coordinate corresponding to a tile center or an actor or object
    mode: Is either 'walk', 'interact' or 'use_skill'
    skill: The skill to be used when mode is set to 'use_skill'.
    """
    if mode == "walk":
        target = tile_center(tile_from_cpos(target))    # Clicked point on ground should target its tile center
    else:
        raise ValueError(f"{mode} not implemented")

    goal = {
        "mode": mode,
        "target": target,
        "skill": skill
    }
    world.goal[actor] = goal
    world.navigation[actor].reset()
    world.navigation[actor].goal = goal


def goal_resolution_system(world):
    """Attempts goal action for actors in range of their target."""
    for actor, goal in list(world.goal.items()):
        goal = world.goal[actor]
        mode = goal["mode"]
        target = goal["target"]

        if mode == "walk":
            goal_reached = world.transform[actor].cpos == target
        else:
            current_tile = tile_from_cpos(world.transform[actor].cpos)
            target_tile = tile_from_cpos(world.transform[target].cpos)
            completion_range = get_goal_completion_range(world, actor)
            goal_reached = in_range_of_goal(current_tile, target_tile, completion_range)

        if goal_reached:
            attempt_goal(world, actor)
            continue

        navigation_failed = world.navigation[actor].failed
        if navigation_failed:
            clear_goal(world, actor)


def attempt_goal(world, actor):
    """
    Attempts to perform the goal action.
    If conditions are met the goal action is performed and the goal is discarded.

    A 'walk' goal is always completed/discarded.
    An 'interact' or 'use_skill' goal must satisfy additional gameplay conditions
        - Actor has adequate skill resources for the given skill, the target is a
         valid recipient of the skill (this check is also performed during goal
         creation), etc.
        - The target interactable is enabled, the actor has permission to use it, etc.
    """
    actor_goal = world.goal[actor]
    mode = actor_goal["mode"]
    target = actor_goal["target"]

    if mode == "walk":
        clear_goal(world, actor)

    elif mode == "interact":
        print(f"Goal completion not implemented: {mode}")

    elif mode == "use_skill":
        skill = actor_goal["skill"]
        print(f"Goal completion not implemented: {mode}")