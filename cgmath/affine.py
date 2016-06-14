from numpy import ndarray

from cgmath.matrix import new_mat4
from cgmath.vector import vec3, vec3_from_scalar
from cgmath.quaternion import quat4f

class Transform(object):
    def __init__(self):
        self._loc = vec3()
        self._rot = quat4f()
        self._scale = vec3_from_scalar(1)

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
        assert isinstance(val, ndarray)
        self._loc = val

    @rot.setter
    def rot(self, val):
        self._rot = val

    @scale.setter
    def scale(self, val):
        assert isinstance(val, ndarray)
        self._scale = val

    def matrix(self):
        # TODO
        return new_mat4(self._scale[0], 0, 0, self._loc[0],
                        0, self._scale[1], 0, self._loc[1],
                        0, 0, self._scale[2], self._loc[2],
                        0, 0, 0, 1)
