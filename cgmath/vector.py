"""Vector/point classes and operations."""

from math import sqrt

import numpy
from numpy import cross, dot
from numpy.linalg import norm


def magnitude_squared(self):
    return self.dot(self)


def magnitude(vec):
    return numpy.linalg.norm(vec)


def distance(self, other):
    return (other - self).length()


def distance_squared(self, other):
    return (other - self).length_squared()


def normalized(vec):
    return vec / magnitude(vec)


def vec2(x=0.0, y=0.0):
    return numpy.array((x, y), numpy.float32)


def copy_xy(dst, src):
    dst[0:2] = src[0:2]


def copy_xyz(dst, src):
    dst[0:3] = src[0:3]


def vec3(x=0.0, y=0.0, z=0.0):
    return numpy.array((x, y, z), numpy.float32)


def vec3_from_scalar(value):
    return vec3(value, value, value)
