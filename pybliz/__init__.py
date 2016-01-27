import cyglfw3 as glfw
from OpenGL import GL as gl
from pybliz.math3d import *
from pybliz.shader import *

glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, 1)
glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

if not glfw.Init():
    exit()


class Scene:
    def __init__(self):
        self._projection_matrix = Mat4x4.identity()
        self._root = SceneNode()
        self._camera = SceneNode()
        self._root.add(self._camera)

    @property
    def projection_matrix(self):
        return self._projection_matrix

    @property
    def root(self):
        return self._root

    def iter_nodes(self, func):
        stack = [self._root]
        while len(stack) != 0:
            node = stack.pop()
            stack += node.children
            func(node)

    def draw(self, viewport_size):
        near = 0.01
        far = 100.0
        self._projection_matrix = Mat4x4.perspective(90,
                                                     viewport_size,
                                                     near, far)

        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT , gl.GL_DEPTH_BUFFER_BIT)

        self.iter_nodes(SceneNode._bake_transform)
        self.iter_nodes(lambda node: node.draw(self))


class SceneNode:
    def __init__(self):
        self._parent = None
        self._children = []
        self._transform = Transform()
        self._baked_transform = Mat4x4()

    def _bake_transform(self):
        mat = self._transform.matrix()
        if self._parent is None:
            self._baked_transform = mat
        else:
            self._baked_transform = self._parent._baked_transform * mat

    @property
    def transform(self):
        return self._transform

    @property
    def children(self):
        return self._children

    def add(self, child):
        child._parent = self
        self._children.append(child)

    def remove(self, child):
        child._parent = None
        self._children.append(child)

    def draw(self, scene):
    #     subdraw = DrawData()
    #     subdraw.projection = draw_data.projection
    #     subdraw.model_view = subdraw.model_view * self._transform.matrix()

    #     for child in self._children:
    #         child.draw(subdraw)

    #     self.draw_self(subdraw)

    # def draw_self(self, draw_data):
        pass


def obj_remove_comment(line):
    ind = line.find('#')
    if ind != -1:
        line = line[:ind].rstrip()
    return line


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

    def draw(self, scene):
        self._program.bind()
        self._program.set_uniform('model_view', self._baked_transform)
        self._program.set_uniform('projection', scene.projection_matrix)

        verts = []

        for face in self.faces:
            vi0 = face.indices[-1]
            for i in range(len(face.indices) - 2):
                vi1 = face.indices[i]
                vi2 = face.indices[i + 1]

                for vi in (vi0, vi1, vi2):
                    vec = self.verts[vi].loc
                    verts += [vec.x, vec.y, vec.z, 1]

        attrib = 0
        attrib_size = 4  # xyzw

        gl.glEnableVertexAttribArray(attrib)

        normalized = False
        stride = 0
        
        gl.glVertexAttribPointer(attrib,
                                 attrib_size,
 	                         gl.GL_FLOAT,
                                 normalized,
                                 stride,
                                 verts)

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(verts) // 3)
        gl.glDisableVertexAttribArray(attrib);


class Window(Scene):
    def __init__(self):
        super().__init__()

        window = glfw.CreateWindow(640, 480, 'pybliz')
        if window:
            glfw.MakeContextCurrent(window)
            self._glfw_window = window
            self._scene = Scene()
        else:
            glfw.Terminate()
            raise RuntimeError('failed to create glfw window')

    def draw(self):
        super().draw(self.viewport_size())

    def viewport_size(self):
        # TODO
        return Vec2(640, 480)

    def glfw_window(self):
        return glfw_window

    def run(self):
        while not glfw.WindowShouldClose(self._glfw_window):
            self.draw()

            # Swap front and back buffers
            glfw.SwapBuffers(self._glfw_window)

            # Poll for and process events
            glfw.PollEvents()
        glfw.Terminate()
