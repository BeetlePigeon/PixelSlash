def snapshot_system(world):
    for transform in world.transform.values():
        transform.prev_cpos = transform.cpos