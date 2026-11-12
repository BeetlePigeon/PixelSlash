from range_utils import in_range_of_goal


def navigation_system(world):
    """Maintains waypoints for actors to pursue their goal. Waypoints
    are generated based on the actor and target positions and usage range
    of the goal action.

    Navigator objects store the actual waypoints and blockage information.
    Navigation system uses navigator state to maintain or create new waypoints."""
    for actor, goal in world.goal.items():
        nav = world.navigation[actor]
        mode = goal["mode"]
        target = goal["target"]
        skill = goal["skill"]

        in_range = in_range_of_goal(world, actor)

        if not in_range:
            if goal["mode"] == "walk":
                if not nav.waypoints:
                    nav.waypoints = generate_waypoints(world, actor, mode, target, skill)
                can_enable_walk = world.walk_controller[actor].request_enable_controller()
                if can_enable_walk:
                    world.walk_controller[actor].enabled = True
            else:
                raise ValueError(f"{mode} not implemented")


def generate_waypoints(world, actor, mode, target, skill):
    if mode == "walk":
        return [target]
    else:
        raise ValueError(f"{mode} not implemented")