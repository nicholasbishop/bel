import cyglfw3 as glfw
from OpenGL import GL as gl

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
        pass


class MeshNode(SceneNode):
    pass


class Window:
    def __init__(self, scene):
        window = glfw.CreateWindow(640, 480, 'pybliz')
        if window:
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
        self._scene.draw()

    def glfw_window(self):
        return glfw_window

    def run(self):
        glfw.MakeContextCurrent(self._glfw_window)
        while not glfw.WindowShouldClose(self._glfw_window):
            self.render()

            # Swap front and back buffers
            glfw.SwapBuffers(self._glfw_window)

            # Poll for and process events
            glfw.PollEvents()
        glfw.Terminate()
