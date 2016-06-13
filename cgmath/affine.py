from cgmath.matrix import mat4f
from cgmath.vector import vec3f
from cgmath.quaternion import quat4f

class Transform(object):
    def __init__(self):
        self._loc = vec3f()
        self._rot = quat4f()
        self._scale = vec3f(1)

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

    def matrix(self):
        # TODO
        return mat4f(self._scale.x, 0, 0, self._loc.x,
                     0, self._scale.y, 0, self._loc.y,
                     0, 0, self._scale.z, self._loc.z,
                     0, 0, 0, 1)
