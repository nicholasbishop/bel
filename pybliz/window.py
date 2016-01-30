from OpenGL import GL as gl

import cyglfw3 as glfw

from pybliz.scene import Scene
from pybliz.math3d import Vec2

glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, 1)
glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

if not glfw.Init():
    exit()

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
        gl.glEnable(gl.GL_DEPTH_TEST)
        x = 0
        while not glfw.WindowShouldClose(self._glfw_window):
            self.draw()

            # Swap front and back buffers
            glfw.SwapBuffers(self._glfw_window)

            # Poll for and process events
            glfw.PollEvents()

            self._root._children[1].transform.set_translation(x, 0, -5)
            x += 0.01
        glfw.Terminate()
