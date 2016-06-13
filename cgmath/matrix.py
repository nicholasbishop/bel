import numpy

class Mat4f:
    """4x4 matrix backed by a numpy float32 matrix."""
    def __init__(self, numpy_matrix):
        assert numpy_matrix.shape == (4, 4)
        assert numpy_matrix.dtype == numpy.float32
        self._matrix = numpy_matrix

    @property
    def numpy_matrix(self):
        return self._matrix

    def __repr__(self):
        return ('Mat4f({: 9.3}, {: 9.3}, {: 9.3}, {: 9.3},\n'
                '      {: 9.3}, {: 9.3}, {: 9.3}, {: 9.3},\n'
                '      {: 9.3}, {: 9.3}, {: 9.3}, {: 9.3},\n'
                '      {: 9.3}, {: 9.3}, {: 9.3}, {: 9.3})'
                ).format(
            *(self._matrix.T.item(n) for n in range(16)))


def mat4f(*args):
    assert len(args) == 16
    return Mat4f(numpy.matrix([args[:4],
                               args[4:8],
                               args[8:12],
                               args[12:]],
                              dtype=numpy.float32).transpose())
