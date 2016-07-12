"""Ray defined by origin and direction."""

class Ray:
    """Ray defined by origin and direction."""
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def __repr__(self):
        return 'Ray(origin={}, direction={})'.format(self.origin,
                                                     self.direction)
