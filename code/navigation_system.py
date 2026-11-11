def navigation_system(world):
    for actor, goal in world.goal.items():
        nav = world.navigation[actor]

        if goal["mode"] == "walk":
            if not nav.waypoints:
                nav.waypoints = [goal["target"]]