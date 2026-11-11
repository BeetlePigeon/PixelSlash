class WalkController:
    def __init__(self):
        self.speed = 122    # Movement budget per tick, in world units.


    def generate_candidates(self, actor, waypoints):
        """
        Candidates generated are tile center coordinates. For now, the only candidate
        generated is the very next waypoint. Later on, alternate candidates can be
        tile centers adjacent to the actor. Responsibility for checking which candidates
        are viable lives with the movement system."""

        candidates = [waypoints[0]]

        return candidates