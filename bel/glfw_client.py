from cyglfw3.compatible import glfwInit, glfwPollEvents

from bel.client import BaseClient

class GlfwClient(BaseClient):
    def __init__(self, log, event_loop, rpc):
        super().__init__(log, event_loop, rpc)
        self._poll_glfw_future = None

    def init_glfw(self):
        if not glfwInit():
            # TODO
            raise NotImplementedError('glfwInit failed')

    def poll_glfw_events(self):
        glfwPollEvents()
        if self._running:
            # TODO
            delay = 1 / 120
            future = self._event_loop.call_later(delay, self.poll_glfw_events)
            self._poll_glfw_future = future

    def xstop(self):
        self._running = False
        self._rpc.stop()
        self._poll_glfw_future.cancel()
