import cyglfw3 as glfw
from OpenGL import GL as gl

if not glfw.Init():
    exit()

class Transform:
    def __init__(self):
        pass

class SceneNode:
    def __init__(self):
        self._children = []
        self._transform = Transform()

    def add(self, child):
        self._children.append(child)

    def remove(self, child):
        self._children.append(child)

    def draw(self):
        pass

class Scene:
    def __init__(self):
        self._root = SceneNode()

    def root(self):
        return self._root

class Window:
    def __init__(self, scene):
        window = glfw.CreateWindow(640, 480, 'pybliz')
        if window:
            self._glfw_window = window
            self._scene = scene
        else:
            glfw.Terminate()
            raise RuntimeError('failed to create glfw window')

    def render(self):
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT , gl.GL_DEPTH_BUFFER_BIT)
        self._scene.root().draw()

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
