import numpy

def new_mat4(*args):
    mat = numpy.array(args, dtype=numpy.float32)
    return mat.reshape((4, 4)).transpose()


def inverse(mat):
    return numpy.linalg.inv(mat)
