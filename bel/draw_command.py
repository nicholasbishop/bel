from OpenGL.GL import GL_LINES, GL_POINTS, GL_TRIANGLES

from bel.auto_name import auto_name
from bel.vertex_array_object import VertexArrayObject

class DrawCommandHandle:
    def __init__(self):
        self._uid = auto_name('drawcmd')
        self.needs_update = True

    @property
    def uid(self):
        return self._uid


class DrawCommand:
    Lines = GL_LINES
    Points = GL_POINTS
    Triangles = GL_TRIANGLES

    def __init__(self):
        self.material_name = 'default'
        self.attributes = {}
        self.uniforms = {}
        self.vert_range = (0, 0)
        self.primitive = self.Points
        self.vao = VertexArrayObject()
