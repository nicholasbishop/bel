from OpenGL.GL import glUniformMatrix4fv, glUniform2fv, glUniform4fv

class MatrixUniform:
    def __init__(self, data):
        self._data = data

    def bind(self, uniform_location):
        count = 1
        transpose = False
        glUniformMatrix4fv(uniform_location, count, transpose, self._data)


class VectorUniform:
    def __init__(self, data):
        self._data = data

    def bind(self, uniform_location):
        count = 1
        if len(self._data) == 2:
            glUniform2fv(uniform_location, count, self._data)
        elif len(self._data) == 4:
            glUniform4fv(uniform_location, count, self._data)
        else:
            raise NotImplementedError(self._data)
