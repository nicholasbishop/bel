from cyglfw3.compatible import (glfwCreateWindow,
                                glfwInit,
                                glfwMakeContextCurrent,
                                glfwPollEvents,
                                glfwSwapBuffers,
                                glfwWindowShouldClose)

from bel.client import BaseClient

class GlfwClient(BaseClient):
    def __init__(self, log, event_loop, rpc):
        super().__init__(log, event_loop, rpc)
        self._poll_glfw_future = None
        self._init_glfw()
        self._poll_glfw_events()
        self._window = None

    def _init_glfw(self):
        if not glfwInit():
            raise RuntimeError('glfwInit failed')
        self._window = glfwCreateWindow(640, 480, "Simple Example")

    def _poll_glfw_events(self):
        self._log.debug('poll glfw events')
        glfwMakeContextCurrent(self._window)
        glfwSwapBuffers(self._window)
        glfwPollEvents()
        if glfwWindowShouldClose(self._window):
            self.stop()
        if self.running:
            # TODO
            delay = 1 / 120
            future = self._event_loop.call_later(delay, self._poll_glfw_events)
            self._poll_glfw_future = future

    def stop(self):
        super().stop()
        if self._poll_glfw_future is not None:
            self._poll_glfw_future.cancel()
