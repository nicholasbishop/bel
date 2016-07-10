from OpenGL.GL import GL_LINES, GL_POINTS, GL_TRIANGLES

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
