def goal_system(world):
    for actor in world.goal:
        handle_goal(world, actor)


def handle_goal(world, actor):
    actor_goal = world.goal[actor]
    mode = actor_goal["mode"]
    target = actor_goal["target"]

    if mode == "walk":
#        print(f"{actor} goal: walk to {target}")
        pass

    elif mode == "interact":
        print(f"{actor} goal: interact with {target}")

    elif mode == "use_skill":
        skill = actor_goal["skill"]
        print(f"{actor} goal: use skill {skill} on {target}")

    else:
        raise ValueError(f"Unsupported goal mode: {mode}")


def set_goal(world, actor, target, mode, skill=None):
    actor_goal = world.goal.get(actor)

    if actor_goal:
        if target == actor_goal["target"] and mode == actor_goal["mode"]:
            return

    world.goal[actor] = {
        "mode": mode,
        "target": target,
        "skill": skill
    }