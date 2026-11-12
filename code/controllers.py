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
        Candidates generated are tile center coordinates. The only candidate
        generated is the waypoint.

        Responsibility for checking which candidates are viable lives with the movement system.

        Future implementation: alternate/secondary candidates based on waypoint.
        """
        return [waypoint]