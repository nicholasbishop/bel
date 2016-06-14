import numpy

def new_mat4(*args):
    return numpy.array((
        args[0], args[4], args[8], args[12],
        args[1], args[5], args[9], args[13],
        args[2], args[6], args[10], args[14],
        args[3], args[7], args[11], args[15],
    ), dtype=numpy.float32)
