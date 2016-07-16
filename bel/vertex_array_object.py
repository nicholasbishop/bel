from OpenGL.GL import glBindVertexArray, glGenVertexArrays

class VertexArrayObject:
    _BoundVertexArrayObject = None

    def __init__(self):
        self._hnd = glGenVertexArrays(1)

    def bind(self):
        if self._hnd != self._BoundVertexArrayObject:
            glBindVertexArray(self._hnd)
            self._BoundVertexArrayObject = self._hnd

    @classmethod
    def unbind(self):
        glBindVertexArray(0)
        self._BoundVertexArrayObject = None
