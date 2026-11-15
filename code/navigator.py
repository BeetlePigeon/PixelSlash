class Navigator:
    """
    Navigator is a container for waypoints and relevant navigation state based on the those waypoints.
    Actual navigation logic happens in the 'navigation_system'.
    """
    def __init__(self, waypoints: list):
        self.waypoints = waypoints
        self.initial_route_planned = False
        self.blocked = False
        self.failed = False


    def reset(self):
        """Resets navigator state."""
        self.waypoints = []
        self.initial_route_planned = False
        self.blocked = False
        self.failed = False