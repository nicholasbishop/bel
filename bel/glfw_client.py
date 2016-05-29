from cyglfw3.compatible import (GLFW_CONTEXT_VERSION_MAJOR,
                                GLFW_CONTEXT_VERSION_MINOR,
                                glfwCreateWindow,
                                glfwDestroyWindow,
                                glfwInit,
                                glfwMakeContextCurrent,
                                glfwPollEvents,
                                glfwSetErrorCallback,
                                glfwSwapBuffers,
                                glfwWindowHint,
                                glfwWindowShouldClose)
from OpenGL.GL import (GL_COLOR_BUFFER_BIT,
                       GL_VERSION,
                       glClear,
                       glClearColor,
                       glGetString)

from bel.client import BaseClient

class GlfwClient(BaseClient):
    def __init__(self, log, event_loop, rpc):
        super().__init__(log, event_loop, rpc)
        self._poll_glfw_future = None
        self._window = None

        self._init_glfw()

    def _cb_glfw_error(self, error, description):
        # TODO
        self._log.error('GLFW error: %d %s', error, description)

    def _init_glfw(self):
        if not glfwInit():
            raise RuntimeError('glfwInit failed')

        glfwSetErrorCallback(self._cb_glfw_error)

        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)

        # TODO
        self._window = glfwCreateWindow(800, 600, 'bel')
        if self._window is None:
            raise RuntimeError('glfwCreateWindow failed')

        glfwMakeContextCurrent(self._window)
        self._log.info('GL_VERSION: %s', glGetString(GL_VERSION))

        self._poll_glfw_events()

    def _draw(self):
        glClearColor(0.4, 0.4, 0.5, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def _poll_glfw_events(self):
        glfwMakeContextCurrent(self._window)
        self._draw()
        glfwSwapBuffers(self._window)
        glfwPollEvents()

        if glfwWindowShouldClose(self._window):
            self.running = False
            self.shutdown()

        if self.running:
            # TODO
            delay = 1 / 120
            future = self._event_loop.call_later(delay, self._poll_glfw_events)
            self._poll_glfw_future = future

    def stop(self):
        if self._window:
            glfwDestroyWindow(self._window)
            self._window = None

        if self._poll_glfw_future is not None:
            self._poll_glfw_future.cancel()

        super().stop()
