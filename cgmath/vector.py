"""Vector/point classes and operations."""

from math import sqrt

import numpy
from numpy import cross, dot
from numpy.linalg import norm


def magnitude_squared(vec):
    return dot(vec, vec)


def magnitude(vec):
    return numpy.linalg.norm(vec)


def distance(vec1, vec2):
    return magnitude(vec1 - vec2)


def distance_squared(vec1, vec2):
    return magnitude_squared(vec1 - vec2)


def normalized(vec):
    return vec / magnitude(vec)


def copy_xy(dst, src):
    dst[0:2] = src[0:2]


def copy_xyz(dst, src):
    dst[0:3] = src[0:3]


def vec2(x=0.0, y=0.0):
    return numpy.array((x, y), numpy.float32)


def vec3(x=0.0, y=0.0, z=0.0):
    return numpy.array((x, y, z), numpy.float32)


def vec4(x=0.0, y=0.0, z=0.0, w=0.0):
    return numpy.array((x, y, z, w), numpy.float32)


def vec3_from_scalar(value):
    return vec3(value, value, value)


def vec3_from_vec4(vec):
    return vec[0:3]


def vec4_from_vec2(vec, z=0.0, w=0.0):
    return vec4(vec[0], vec[1], z, w)
