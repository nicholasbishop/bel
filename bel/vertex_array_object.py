from OpenGL.GL import glBindVertexArray, glGenVertexArrays

class VertexArrayObject:
    _BoundVertexArrayObject = None

    def __init__(self):
        self._hnd = glGenVertexArrays(1)

    def bind(self):
        if self._hnd != VertexArrayObject._BoundVertexArrayObject:
            glBindVertexArray(self._hnd)
            VertexArrayObject._BoundVertexArrayObject = self._hnd

    @classmethod
    def unbind(cls):
        glBindVertexArray(0)
        cls._BoundVertexArrayObject = None
