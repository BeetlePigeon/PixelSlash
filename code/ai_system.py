from goal_resolution_system import set_goal


def ai_system(world):
    for eid, ai in world.ai.items():
        if world.tick - ai["last_think"] < ai["think_cooldown"]:
            continue

        goal = world.goal.get(eid, None)
        if not goal:
            ai["last_think"] = world.tick
            target = world.player
            set_goal(world, actor=eid, target=target, mode="use_skill", skill="attack")