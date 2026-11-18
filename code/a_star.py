import heapq
from constants import WORLD_UNITS
from support import tile_from_cpos
from occupancy_utils import get_footprint_tiles
from objects import Vec2i


# Octile distance: orthogonal to diagonal is 1:sqrt(2) ~ 10:14
ORTH_COST = 10
DIAG_COST = 14

DIRECTIONS = [
    (Vec2i(1, 0), ORTH_COST),    # East
    (Vec2i(-1, 0), ORTH_COST),   # West
    (Vec2i(0, 1), ORTH_COST),    # South
    (Vec2i(0, -1), ORTH_COST),   # North
    (Vec2i(1, 1), DIAG_COST),  # Southeast
    (Vec2i(-1, -1), DIAG_COST),  # Northwest
    (Vec2i(-1, 1), DIAG_COST),  # Southwest
    (Vec2i(1, -1), DIAG_COST),  # Northeast
]


def heuristic(start, goal):
    dx = abs(goal.x - start.x)
    dy = abs(goal.y - start.y)
    return ORTH_COST * max(dx, dy) + (DIAG_COST - ORTH_COST) * min(dx, dy)


def multi_goal_heuristic(current, goals):
    return min(heuristic(current, goal) for goal in goals)


def get_legal_neighbors(world, current, actor_tiles, footprint):
    """
    Gets legal neighbor tiles for the expanded tile node.
    Legal neighbors are tiles where the actor can stand.
    """
    for dir, move_cost in DIRECTIONS:
        neighbor = current + dir
        if not (0 <= neighbor.x < world.map_width and 0 <= neighbor.y < world.map_height):
            continue
        if footprint == "single":
            if neighbor in world.single_static_blockers:
                continue
            if world.single_dynamic_blockers[neighbor] > (neighbor in actor_tiles):
                continue
        elif footprint == "plus":
            if neighbor in world.plus_static_blockers:
                continue
            if world.plus_dynamic_blockers[neighbor] > (neighbor in actor_tiles):
                continue
        yield neighbor, move_cost


def tiles_to_positions(path):
    """Turns the list of tiles into a list of tile centers."""
    return [Vec2i(WORLD_UNITS // 2 + tile.x * WORLD_UNITS, WORLD_UNITS//2 + tile.y * WORLD_UNITS) for tile in path]


def reconstruct_path(came_from, start, goal):
    """Reconstructs the path into a list of tiles."""
    path = []
    current = goal

    while current != start:
        path.append(current)
        current = came_from[current]

    path.append(start)
    path.reverse()

    return tiles_to_positions(path)


def single_a_star(world, actor, start: Vec2i, goal: Vec2i, footprint: str, max_expansions=700) -> list | None:
    """
    Performs A* to find a path from the start tile to any of the goal tiles.

    args:
    'actor': The actor the A* search is for.
    'start': Starting tile of the search.
    'goal': Goal tile of the search.
    'footprint': The actor's footprint. Is either "single" or "plus".
    'max_expansions': How many nodes the algorithm may expand before aborting.

    returns:
    A list of tile center Vec2i's for a successful path or 'None' if A* failed.
    """
    if not (0 <= start.x < world.map_width and 0 <= start.y < world.map_height):
        return None

    if not (0 <= goal.x < world.map_width and 0 <= goal.y < world.map_height):
        return None

    center, wings = get_footprint_tiles(world.transform[actor].cpos, footprint)
    actor_tiles = [center, *wings]

    if footprint == "single":
        if goal in world.single_static_blockers:
            return None
        if world.single_dynamic_blockers[goal] > (goal in actor_tiles):
            return None
    elif footprint == "plus":
        if goal in world.plus_static_blockers:
            return None
        if world.plus_dynamic_blockers[goal] > (goal in actor_tiles):
            return None

    frontier = [(heuristic(start, goal), 0, start)]
    g_score = {start: 0}
    came_from = {}
    nodes_expanded = 0  # profiling metric

    while frontier and nodes_expanded < max_expansions:
        f, g, current = heapq.heappop(frontier)

        if g != g_score[current]:
            continue

        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor, move_cost in get_legal_neighbors(world, current, actor_tiles, footprint):
            new_cost = g_score[current] + move_cost

            if neighbor not in g_score or new_cost < g_score[neighbor]:
                g_score[neighbor] = new_cost
                came_from[neighbor] = current
                h = heuristic(neighbor, goal)
                f = new_cost + h
                heapq.heappush(frontier, (f, new_cost, neighbor))

    return None


def multi_a_star(world, actor, start: Vec2i, goals: list[Vec2i], footprint: str, max_expansions=700) -> list | None:
    """
    Performs A* to find a path from the start tile to any of the goal tiles.

    args:
    'actor': The actor the A* search is for.
    'start': Starting tile of the search.
    'goal': Goal tile of the search.
    'footprint': The actor's footprint. Is either "single" or "plus".
    'max_expansions': How many nodes the algorithm may expand before aborting.

    returns:
    A list of tile center Vec2i's for a successful path or 'None' if A* failed.
    """
    if not (0 <= start.x < world.map_width and 0 <= start.y < world.map_height):
        return None

    for goal in goals:
        if not (0 <= goal.x < world.map_width and 0 <= goal.y < world.map_height):
            return None

        center, wings = get_footprint_tiles(world.transform[actor].cpos, footprint)
        actor_tiles = [center, *wings]

        if footprint == "single":
            if goal in world.single_static_blockers:
                return None
            if world.single_dynamic_blockers[goal] > (goal in actor_tiles):
                return None
        elif footprint == "plus":
            if goal in world.plus_static_blockers:
                return None
            if world.plus_dynamic_blockers[goal] > (goal in actor_tiles):
                return None

        frontier = [(heuristic(start, goal), 0, start)]
        g_score = {start: 0}
        came_from = {}
        nodes_expanded = 0  # profiling metric

        while frontier and nodes_expanded < max_expansions:
            f, g, current = heapq.heappop(frontier)

            if g != g_score[current]:
                continue

            nodes_expanded += 1

            if current in goals:
                return reconstruct_path(came_from, start, goal)

            for neighbor, move_cost in get_legal_neighbors(world, current, actor_tiles, footprint):
                new_cost = g_score[current] + move_cost

                if neighbor not in g_score or new_cost < g_score[neighbor]:
                    g_score[neighbor] = new_cost
                    came_from[neighbor] = current
                    h = heuristic(neighbor, goal)
                    f = new_cost + h
                    heapq.heappush(frontier, (f, new_cost, neighbor))

    return None