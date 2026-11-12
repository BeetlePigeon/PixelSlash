from support import tile_center, tile_from_cpos
from navigation_system import in_range_of_goal


def set_goal(world, actor, target, mode, skill=None):
    """
    Sets the goal of the actor. Goals span a period of time and describe what the actor is
     trying to accomplish in the near future. An actor can only have one goal at a time. Goal
     does not produce waypoints. Navigation produces waypoints based on goal.

    actor: The entity whose goal is being assigned
    target: Is either a world coordinate corresponding to a tile center or an actor or object
    mode: Is either 'walk', 'interact' or 'use_skill'
    skill: The skill to be used when mode is set to 'use_skill'.
    """
    if mode == "walk":
        target = tile_center(tile_from_cpos(target))    # Clicked point on ground should target its tile center

    world.goal[actor] = {
        "mode": mode,
        "target": target,
        "skill": skill
    }
    world.navigation[actor].waypoints.clear()


def goal_resolution_system(world):
    """If the actor is in range of its goal: attempt to perform
    the goal action. Completed goals are discarded and navigation is cleared."""
    for actor, goal in world.goal.items():
        if in_range_of_goal(world, actor):
            handle_goal(world, actor)


def handle_goal(world, actor):
    """
    Attempts to perform the goal action when the actor is in range of its goal.
    Called by goal_resolution_system. The goal action is performed and the goal is discarded.
    """
    actor_goal = world.goal[actor]
    mode = actor_goal["mode"]
    target = actor_goal["target"]

    if mode == "walk":
        world.navigation[actor].waypoints.clear()
        del world.goal[actor]

    elif mode == "interact":
        print(f"Goal completion not implemented: {mode}")

    elif mode == "use_skill":
        skill = actor_goal["skill"]
        print(f"Goal completion not implemented: {mode}")