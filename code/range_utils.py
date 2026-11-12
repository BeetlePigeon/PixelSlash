def in_range_of_goal(world, actor):
    goal = world.goal[actor]
    mode = goal["mode"]
    target = goal["target"]
    skill = goal["skill"]

    if mode == "walk":
        if world.transform[actor].cpos == target:
            return True
        else:
            return False