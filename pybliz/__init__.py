import cyglfw3 as glfw
from OpenGL import GL as gl

glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, 1)
glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

if not glfw.Init():
    exit()

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z


class Quat:
    def __init__(self):
        pass


class Transform:
    def __init__(self):
        self._translation = Vec3(0, 0, 0)
        self._scale = Vec3(1, 1, 1)
        self._rotation = Quat()


class SceneNode:
    def __init__(self):
        self._parent = None
        self._children = []
        self._transform = Transform()

    def add(self, child):
        child._parent = self
        self._children.append(child)

    def remove(self, child):
        child._parent = None
        self._children.append(child)

    def draw(self):
        for child in self._children:
            child.draw()
        self.draw_self()

    def draw_self(self):
        pass


def obj_remove_comment(line):
    ind = line.find('#')
    if ind != -1:
        line = line[:ind].rstrip()
    return line


def extract_uniforms(source):
    for line in source.splitlines():
        parts = line.split()
        if len(parts) > 0 and parts[0] == 'uniform':
            yield parts[2]


class Shader:
    def __init__(self, path, kind):
        self._hnd = gl.glCreateShader(kind)
        if self._hnd == 0:
            raise ValueError('glCreateShader failed')
        with open(path) as rfile:
            source = rfile.read()
            gl.glShaderSource(self._hnd, source)
        gl.glCompileShader(self._hnd)
        if gl.glGetShaderiv(self._hnd, gl.GL_COMPILE_STATUS) == False:
            log = gl.glGetShaderInfoLog(self._hnd)
            gl.glDeleteShader(self._hnd)
            raise RuntimeError('shader failed to compile', log)
        self._uniforms = list(extract_uniforms(source))


class VertexShader(Shader):
    def __init__(self, path):
        super().__init__(path, gl.GL_VERTEX_SHADER)


class FragmentShader(Shader):
    def __init__(self, path):
        super().__init__(path, gl.GL_FRAGMENT_SHADER)


class Program:
    def __init__(self, vertex_shader, fragment_shader):
        self._vs = vertex_shader
        self._fs = fragment_shader
        self._hnd = gl.glCreateProgram()
        if self._hnd == 0:
            raise ValueError('glCreateProgram failed')
        gl.glAttachShader(self._hnd, self._vs._hnd)
        gl.glAttachShader(self._hnd, self._fs._hnd)
        gl.glLinkProgram(self._hnd)

    def bind(self):
        gl.glUseProgram(self._hnd)

    def set_uniform(self):
        pass


class ShaderManager:
    def __init__(self):
        pass


class MeshNode(SceneNode):
    class Vert:
        def __init__(self, loc):
            self.loc = loc

    class Face:
        def __init__(self, indices):
            self.indices = indices

    def __init__(self):
        super().__init__()
        self.verts = []
        self.faces = []
        self._program = Program(VertexShader('shaders/vert.glsl'),
                                FragmentShader('shaders/frag.glsl'))

    @staticmethod
    def load_obj(path):
        with open(path) as rfile:
            verts = []
            faces = []
            for line in rfile.readlines():
                line = obj_remove_comment(line)
                parts = line.split()
                if len(parts) == 0:
                    continue
                tok = parts[0]
                if tok == 'v':
                    vec = Vec3()
                    if len(parts) > 1:
                        vec.x = float(parts[1])
                    if len(parts) > 2:
                        vec.y = float(parts[2])
                    if len(parts) > 3:
                        vec.z = float(parts[3])
                    verts.append(MeshNode.Vert(vec))
                elif tok == 'f':
                    indices = [int(ind) - 1 for ind in parts[1:]]
                    faces.append(MeshNode.Face(indices))
                
            mesh = MeshNode()
            mesh.verts = verts
            mesh.faces = faces
            return mesh

    def draw(self):
        self._program.bind()
        gl.glBegin(gl.GL_TRIANGLES)

        for face in self.faces:
            vi0 = face.indices[-1]
            for i in range(len(face.indices) - 2):
                vi1 = face.indices[i]
                vi2 = face.indices[i + 1]

                for vi in (vi0, vi1, vi2):
                    vec = self.verts[vi].loc
                    gl.glVertex3f(vec.x, vec.y, vec.z)

        gl.glEnd()


class Window:
    def __init__(self):
        window = glfw.CreateWindow(640, 480, 'pybliz')
        if window:
            glfw.MakeContextCurrent(window)
            self._glfw_window = window
            self._root = SceneNode()
            self._camera = SceneNode()
            self._root.add(self._camera)
        else:
            glfw.Terminate()
            raise RuntimeError('failed to create glfw window')

    def scene(self):
        return self._root

    def render(self):
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT , gl.GL_DEPTH_BUFFER_BIT)
        self._root.draw()

    def glfw_window(self):
        return glfw_window

    def run(self):
        while not glfw.WindowShouldClose(self._glfw_window):
            self.render()

            # Swap front and back buffers
            glfw.SwapBuffers(self._glfw_window)

            # Poll for and process events
            glfw.PollEvents()
        glfw.Terminate()
