"""Quaternion class."""

import numpy

# pylint: disable=invalid-name,missing-docstring

class Quat4f(object):
    """Quaternion backed by a numpy float32 array."""

    def __init__(self, numpy_array):
        assert len(numpy_array) == 4
        assert numpy_array.dtype == numpy.float32
        self._array = numpy_array

    @property
    def array(self):
        return self._array

    @array.setter
    def array(self, array):
        self._array = array

    @property
    def vector(self):
        """The vector part of the quaternion."""
        return self._array[0:3]

    @property
    def scalar(self):
        """The scalar part of the quaternion."""
        return self._array[3]


def quat4f(i=0.0, j=0.0, k=0.0, w=1.0):
    return Quat4f(numpy.array((i, j, k, w), numpy.float32))
