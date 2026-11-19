class Navigator:
    """
    Navigator is a container for waypoints and relevant navigation state based on the those waypoints.
    Actual navigation logic happens in the 'navigation_system'.
    """
    def __init__(self, actor, waypoints: list):
        self.actor = actor
        self.goal_tile_center = None
        self.goal_center_reached = False
        self.waypoints = waypoints
        self.initial_route_planned = False
        self.blocked = False
        self.failed = False


    def reset(self, world):
        """Resets navigator state."""
        self.goal_tile_center = None
        self.goal_center_reached = False
        self.waypoints = []
        self.initial_route_planned = False
        self.blocked = False
        self.failed = False
        if self.actor in world.pf_requests:
            del world.pf_requests[self.actor]