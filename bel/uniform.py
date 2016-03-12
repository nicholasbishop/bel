from OpenGL.GL import glUniformMatrix4fv

class MatrixUniform:
    def __init__(self, data):
        self._data = data

    def bind(self, uniform_location):
        count = 1
        transpose = False
        if self._data.shape == (4, 4):
            glUniformMatrix4fv(uniform_location, count, transpose, self._data)
        else:
            raise NotImplementedError()
