import numpy


def new_mat4(*args):
    assert len(args) == 16
    return numpy.matrix([args[:4],
                         args[4:8],
                         args[8:12],
                         args[12:]],
                        dtype=numpy.float32).transpose()
