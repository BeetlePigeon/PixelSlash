class WalkController:
    def __init__(self):
        self.enabled = False
        self.speed = 122    # Movement budget per tick, in world units.


    def generate_candidates(self, pos, waypoint):
        """
        Candidates generated are tile center coordinates. For now, the only candidate
        generated is the very next waypoint. Later on, alternate candidates can be
        tile centers adjacent to the actor. Responsibility for checking which candidates
        are viable lives with the movement system."""
        return [waypoint]


    def request_enable_controller(self):
        """Movement system only processes enabled motion controllers. Navigation system
        can request enabling of controller.

        Future implementation: This request can be denied by actors being in certain action states."""
        return True