class Navigator:
    """
    Navigator is the container for waypoints and action range (computed during goal generation)
    for the actor's goal and blocked state. Navigation logic happens in the 'navigation_system'.
    """
    def __init__(self, waypoints: list):
        self.waypoints = waypoints
        self.completion_range = 0  # Tile distance to be in range of goal
        self.goal = None
        self.initial_route_planned = False
        self.blocked = False


    def clear_navigator(self, world, actor):
        """Clears navigator state. Called by 'goal_system' when the current goal is discarded."""
        self.waypoints = []
        self.completion_range = 0
        self.goal = None
        self.initial_route_planned = False
        self.blocked = False