import heapq
from constants import WORLD_UNITS
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


def get_legal_neighbors(world, current, footprint):
    """
    Gets legal neighbor tiles for the expanded tile node.
    Legal neighbors are tiles where the actor can stand.
    """
    for dir, move_cost in DIRECTIONS:
        neighbor = current + dir
        if not (0 <= neighbor.x < world.map_width and 0 <= neighbor.y < world.map_height):
            continue
        if footprint == "single":
            if neighbor in world.single_static_blockers or world.single_dynamic_blockers[neighbor] > 0:
                continue
        elif footprint == "plus":
            if neighbor in world.plus_static_blockers or world.plus_dynamic_blockers[neighbor] > 0:
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


def a_star(world, start: Vec2i, goal: Vec2i, footprint: str, max_expansions=700) -> list | None:
    """
    Performs A* to find a path from the start tile to the goal tile.
    WARNING!
        Currently only considers static blockages when evaluating tile legality.
    Considers diagonal tiles blocked if either adjacent orthogonal tile is blocked (even if the diagonal tile is legal.)
    Uses octile distance for the heuristic.

    args:
    'start': Starting tile of the search.
    'goal': Goal tile of the search.
    'max_expansions': How many nodes the algorithm may expand before aborting.

    returns:
    A list of tile center Vec2i's for a successful path or an empty list if A* failed.
    """
    if goal in world.plus_static_blockers:
        return None

    if not (0 <= start.x < world.map_width and 0 <= start.y < world.map_height):
        return None

    if not (0 <= goal.x < world.map_width and 0 <= goal.y < world.map_height):
        return None

    frontier = [(heuristic(start, goal), 0, start)]
    g_score = {start: 0}
    came_from = {}
    nodes_expanded = 0  # profiling metric

    while frontier and nodes_expanded < max_expansions:
        f, g, current = heapq.heappop(frontier)
        nodes_expanded += 1

        if g != g_score[current]:
            continue

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor, move_cost in get_legal_neighbors(world, current, footprint):
            new_cost = g_score[current] + move_cost

            if neighbor not in g_score or new_cost < g_score[neighbor]:
                g_score[neighbor] = new_cost
                came_from[neighbor] = current
                h = heuristic(neighbor, goal)
                f = new_cost + h
                heapq.heappush(frontier, (f, new_cost, neighbor))

    return None