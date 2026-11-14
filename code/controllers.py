from support import tile_from_cpos, tile_center, tiles_traversed


class WalkController:
    """"
    WalkController generates movement candidates based on the current waypoint.
    It has no knowledge of the actor goal or navigation.
    """
    def __init__(self):
        self.enabled = False
        self.speed = 122    # Movement budget per tick, in world units.


    def generate_candidates(self, pos, waypoint):
        """
        Candidates generated are tile center coordinates.
        The first candidate generated is the waypoint itself.

        Responsibility for checking which candidates are viable lives with the movement system.

        args
        'pos': The actor's position.
        'waypoint': The waypoint the candidates are being generated for.
        'first_crossing': The center of the first tile passed into if continuing in direction of waypoint.
        'left_of_first_crossing': The center of the tile to the left of 'first_crossing' tile (facing the waypoint).
        'right_of_first_crossing': The center of the tile to the right of 'first_crossing' tile (facing the waypoint.

        Future implementation: alternate/secondary candidates based on waypoint.
        """
        candidates = []
        direct_to_waypoint = waypoint
#        candidates.append(direct_to_waypoint)

        tiles_crossed = tiles_traversed(pos, waypoint)
        if tiles_crossed:
            first_crossing_tile = tiles_crossed[0]
            first_crossing_center = tile_center(first_crossing_tile)
            first_crossing_direction = first_crossing_tile - tile_from_cpos(pos)

            left_of_first_crossing = first_crossing_direction.rotate_90_ccw()
            left_tile = first_crossing_tile + left_of_first_crossing
            left_tile_center = tile_center(left_tile)

            right_of_first_crossing = first_crossing_direction.rotate_90_cw()
            right_tile = first_crossing_tile + right_of_first_crossing
            right_tile_center = tile_center(right_tile)

            if first_crossing_tile not in candidates:
                candidates.append(first_crossing_center)
            if left_tile not in candidates:
                candidates.append(left_tile_center)
            if right_tile not in candidates:
                candidates.append(right_tile_center)

        return candidates