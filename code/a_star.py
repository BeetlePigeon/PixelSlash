import heapq
from constants import WORLD_UNITS
from occupancy_utils import get_footprint_tiles
from objects import Vec2i
from profiler import timed


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


@timed
def bounded_a_star(world, actor,
                   start: Vec2i, goal: Vec2i, footprint,
                   bounds, max_expansions) -> list | None:
    """
    Performs A* to find a path from the start tile to the closest tile to the goal within the bounds given.

    args:
    'world': The game World object.
    'actor': The actor the A* search is for.
    'start': Starting tile of the search.
    'goal': The tile the target is currently on. Used for the heuristic.
    'footprint': The actor's footprint. Is either "single" or "plus".
    'bounds': An N x N box centered at 'start' that the search must stay within.
    'max_expansions': How many nodes the algorithm may expand before aborting.

    returns:
    A list of tile center Vec2i's for a successful path or 'None' if A* failed.
    """
    if not (0 <= start.x < world.map_width and 0 <= start.y < world.map_height):
        return None  # No path for out of bounds tiles can exist

    def in_bounds(tile):
        minimum, maximum = bounds
        return (
            minimum.x <= tile.x <= maximum.x and
            minimum.y <= tile.y <= maximum.y
        )

    center, wings = get_footprint_tiles(world.transform[actor].cpos, footprint)
    actor_tiles = {center, *wings}

    # Filter goals: no out of bounds tiles
    if not (0 <= goal.x < world.map_width and 0 <= goal.y < world.map_height):
        return None

    best_partial = start
    best_partial_score = (heuristic(start, goal), 0)

    # Initialize one A* search
    frontier = [(heuristic(start, goal), 0, start)]  # f, g, node
    g_score = {start: 0}    # node: g
    came_from = {}  # node: parent
    nodes_expanded = 0  # profiling metric

    best_goal = None
    best_score = float("inf")
    while frontier and nodes_expanded < max_expansions:
        f, g, current = heapq.heappop(frontier)
        if g != g_score[current]:
            continue    # Ignore outdated priority-queue entries.
        if f >= best_score:
            break   # No remaining path can improve the best solution.

        nodes_expanded += 1

        score = (heuristic(current, goal), g)
        if score < best_partial_score:
            best_partial = current
            best_partial_score = score

        if current == goal:
            if g < best_score:
                best_score = score
                best_goal = current

        for neighbor, move_cost in get_legal_neighbors(world, current, actor_tiles, footprint):
            if not in_bounds(neighbor):
                continue

            new_cost = g + move_cost

            if new_cost < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = new_cost
                came_from[neighbor] = current
                f = new_cost + heuristic(neighbor, goal)
                heapq.heappush(frontier, (f, new_cost, neighbor))

    if best_goal is not None:
        return reconstruct_path(came_from, start, best_goal)

    if best_partial != start:
        return reconstruct_path(came_from, start, best_partial)

    return None


@timed
def multigoal_a_star(world, actor, start: Vec2i, goals: list[Vec2i],
                     central_tile, footprint: str, max_expansions, weight) -> list | None:
    """
    Performs A* to find a path from the start tile to the best legal goal tile.
    Goal tiles are potential engagement positions.
    The chosen heuristic balances distance from actor to goal against distance from goal to target so that actors
    tend to form denser packs on the approaching side before fanning out and surrounding the target.

    args:
    'world': The game World object.
    'actor': The actor the A* search is for.
    'start': Starting tile of the search.
    'goals': Potential goal tiles of the search (checked for legality during search, not before.)
    'central_tile': The tile the target is currently on. Used for the heuristic.
    'footprint': The actor's footprint. Is either "single" or "plus".
    'max_expansions': How many nodes the algorithm may expand before aborting.
    'weight': A tuning parameter used for the heuristic. Balances cost of path from actor to goal against
     cost of path from goal to target.

    returns:
    A list of tile center Vec2i's for a successful path or 'None' if A* failed.
    """
    if not (0 <= start.x < world.map_width and 0 <= start.y < world.map_height):
        return None        # No path for out of bounds tiles can exist

    center, wings = get_footprint_tiles(world.transform[actor].cpos, footprint)
    actor_tiles = {center, *wings}
    valid_goals = set()

    for goal in goals:
        # Filter goals: no out of bounds or obstructed tiles
        if not (0 <= goal.x < world.map_width and 0 <= goal.y < world.map_height):
            continue
        if footprint == "single":
            if goal in world.single_static_blockers:
                continue
            if world.single_dynamic_blockers[goal] > (goal in actor_tiles):
                continue
        elif footprint == "plus":
            if goal in world.plus_static_blockers:
                continue
            if world.plus_dynamic_blockers[goal] > (goal in actor_tiles):
                continue
        valid_goals.add(goal)

    if not valid_goals:
        return None

    penalties = {
        goal: weight * heuristic(goal, central_tile)
        for goal in valid_goals
    }

    def weighted_h(node):
        return min(heuristic(node, goal) + penalties[goal]
                   for goal in valid_goals)

    # Initialize one A* search
    frontier = [(weighted_h(start), 0, start)]  # f, g, node
    g_score = {start: 0}    # node: g
    came_from = {}  # node: parent
    nodes_expanded = 0  # profiling metric

    best_goal = None
    best_score = float("inf")
    while frontier and nodes_expanded < max_expansions:
        f, g, current = heapq.heappop(frontier)
        if g != g_score[current]:
            continue    # Ignore outdated priority-queue entries.
        if f >= best_score:
            break   # No remaining path can improve the best solution.

        nodes_expanded += 1

        if current in valid_goals:
            score = g + penalties[current]
            if score < best_score:
                best_score = score
                best_goal = current

        for neighbor, move_cost in get_legal_neighbors(world, current, actor_tiles, footprint):
            new_cost = g + move_cost
            if new_cost < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = new_cost
                came_from[neighbor] = current
                f = new_cost + weighted_h(neighbor)
                heapq.heappush(frontier, (f, new_cost, neighbor))

    if best_goal is not None:
        return reconstruct_path(came_from, start, best_goal)

    return None