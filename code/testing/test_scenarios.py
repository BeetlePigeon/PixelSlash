from objects import Vec2i


def open_chase_spawns():
    tiles = []
    for y in range(1, 6):
        for x in range(1, 11):
            spawn_x = (2 * x)
            spawn_y = (2 * y)
            tiles.append(Vec2i(spawn_x, spawn_y))
    return tiles


def collapse_inward_spawns():
    return [
        Vec2i(5, 5),
        Vec2i(7, 7),
        Vec2i(5, 7),
        Vec2i(7, 5),
        Vec2i(5, 9),
    ]


open_chase = {
    "area_map": "open_map",
    "enemy_positions": open_chase_spawns(),
    "inputs": {
            32: [("move_mouse", (320, 50))],
            33: [("mouse_press", 0)],
            34: [("mouse_release", 0)],
            500: [("move_mouse", (20, 450))],
            501: [("mouse_press", 0)],
            502: [("mouse_release", 0)],
        }
    }


collapse_inwards = {
    "area_map": "collapse_scenario_map",
    "enemy_positions": collapse_inward_spawns(),
    "inputs": {
        32: [("move_mouse", (350, 300))],
        33: [("mouse_press", 0)],
        34: [("mouse_release", 0)],
        300: [("move_mouse", (290, 180))],
        301: [("mouse_press", 0)],
        302: [("mouse_release", 0)],
    }
}


scenarios = {
    "open_chase": open_chase,
    "collapse_inwards": collapse_inwards,
}