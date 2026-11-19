from support import tile_center, tile_from_cpos
from goal_utils import in_range_of_goal, clear_goal, get_goal_completion_range


def set_goal(world, actor, target, mode, skill=None):
    """
    Sets the goal of the actor.

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
    elif mode == "interact":
        pass
    else:
        pass

    goal = {
        "mode": mode,
        "target": target,
        "skill": skill
    }

    curr_goal = world.goal.get(actor, None)
    if curr_goal and goal == curr_goal:
        return

    world.goal[actor] = goal
    world.navigation[actor].reset()


def goal_resolution_system(world):
    """
    Attempts goal action for actors in who have reached their goal position and are in completion range of their goal
    and discards goals when navigation fails.

    Being at the goal position is different from being in completion range. For example, an actor can be at their goal
    position but their target may have moved out of completion range during the same tick.
    """
    for actor, goal in list(world.goal.items()):
        at_goal_center = world.navigation[actor].goal_center_reached
        in_completion_range = in_range_of_goal(world, actor)

        can_attempt_goal = at_goal_center and in_completion_range

        if can_attempt_goal:
            attempt_goal(world, actor)
            continue

        navigation_failed = world.navigation[actor].failed
        if navigation_failed:
            clear_goal(world, actor)


def attempt_goal(world, actor):
    """
    Attempts to perform the goal action.
    If conditions are met the goal action is performed and the goal is discarded.

    A 'walk' goal has no action and is immediately discarded.
    An 'interact' or 'use_skill' goal must satisfy additional gameplay conditions
        - Actor has adequate skill resources for the given skill, the target is a
         valid recipient of the skill (this check is also performed during goal
         creation), etc.
        - The target interactable is enabled, the actor has permission to use it, etc.
    """
    actor_goal = world.goal[actor]
    mode = actor_goal["mode"]

    if mode == "walk":
        clear_goal(world, actor)

    elif mode == "interact":
        print(f"Chest opened! {world.tick}")
        clear_goal(world, actor)

    elif mode == "use_skill":
        actor_is_ai = world.ai.get(actor, False)
        if actor_is_ai:
            world.ai[actor]["last_think"] = world.tick
        clear_goal(world, actor)