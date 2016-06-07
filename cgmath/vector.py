"""Vector/point classes and operations."""

from math import sqrt

import numpy

# pylint: disable=invalid-name,missing-docstring

class Vec3f(object):
    """3-D point or vector backed by a numpy float32 array."""

    def __init__(self, numpy_array):
        assert len(numpy_array) == 3
        assert numpy_array.dtype == numpy.float32
        self._array = numpy_array

    @property
    def x(self):
        return self._array[0]

    @x.setter
    def x(self, val):
        self._array[0] = val

    @property
    def y(self):
        return self._array[1]

    @y.setter
    def y(self, val):
        self._array[1] = val

    @property
    def z(self):
        return self._array[2]

    @z.setter
    def z(self, val):
        self._array[2] = val

    @property
    def array(self):
        return self._array

    @array.setter
    def array(self, array):
        self._array = array

    def as_tuple(self):
        return (self._array[0], self._array[1], self._array[2])

    def dot(self, other):
        return numpy.dot(self._array, other.array)

    @property
    def length_squared(self):
        return self.dot(self)

    @property
    def length(self):
        return sqrt(self.length_squared)

    @property
    def normalized(self):
        length = self.length
        return Vec3f(self._array / length)

    def __add__(self, other):
        return Vec3f(self._array + other.array)

    def __sub__(self, other):
        return Vec3f(self._array - other.array)


def vec3f(x=0.0, y=0.0, z=0.0):
    return Vec3f(numpy.array((x, y, z), numpy.float32))
