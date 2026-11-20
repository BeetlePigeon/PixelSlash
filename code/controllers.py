class WalkController:
    """"
    WalkController stores state of whether the actor's actual motion is enabled or not and the speed in world units
    at which it locomotes towards goals.
    """
    def __init__(self, speed):
        self.enabled = False
        self.speed = speed    # Movement budget per tick, in world units.