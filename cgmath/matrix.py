import numpy

from cgmath.vector import cross, dot, normalized


# TODO, naming
def new_mat4(*args):
    mat = numpy.array(args, dtype=numpy.float32)
    return mat.reshape((4, 4)).transpose()


def mat4(*args):
    return new_mat4(*args)


def inverse(mat):
    return numpy.linalg.inv(mat)


def mat4_look_at(eye, target, up):
    forward = normalized(eye - target)
    side = normalized(cross(up, forward))
    up = normalized(cross(forward, side))

    return new_mat4(   side[0],    side[1],    side[2], -dot(side, eye),
                         up[0],      up[1],      up[2], -dot(up, eye),
                    forward[0], forward[1], forward[2], -dot(forward, eye),
                             0,          0,          0,  1)
