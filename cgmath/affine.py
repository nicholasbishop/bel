class Transform(object):
    def __init__(self):
        self._loc = vec3f()
        self._rot = quat4f()
        self._scale = vec3f()

    @property
    def loc(self):
        """Location vector."""
        return self._loc

    @property
    def rot(self):
        """Rotation quaternion."""
        return self._loc

    @property
    def scale(self):
        """Scale vector."""
        return self._scale

    @loc.setter
    def loc(self, val):
        self._loc = val

    @rot.setter
    def rot(self, val):
        self._rot = val

    @scale.setter
    def scale(self, val):
        self._scale = val

    @property
    def matrix(self):
        raise NotImplementedError
