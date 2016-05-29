from asyncio import get_event_loop, open_unix_connection, sleep
import logging
import sys

from cyglfw3.compatible import glfwInit, glfwPollEvents

from bel.ipc import JsonRpc
from bel import log

class GlfwClient:
    def __init__(self, event_loop, rpc):
        rpc.set_handler(self)
        self._rpc = rpc
        self._running = True
        self._event_loop = event_loop
        self._poll_glfw_future = None

    def init_glfw(self):
        glfwInit()

    def poll_glfw_events(self):
        glfwPollEvents()
        if self._running:
            # TODO
            delay = 1 / 120
            future = self._event_loop.call_later(delay, self.poll_glfw_events)
            self._poll_glfw_future = future

    def stop(self):
        self._running = False
        self._rpc.stop()
        self._poll_glfw_future.cancel()


async def connect(event_loop, socket_path):
    reader, writer = await open_unix_connection(socket_path)

    rpc = JsonRpc('bel.glfw_client', reader, writer)
    return GlfwClient(event_loop, rpc)


def main():
    socket_path = sys.argv[1]
    logging.info('starting child, socket path: %s', socket_path)

    event_loop = get_event_loop()

    get_event_loop().set_debug(True)

    client = event_loop.run_until_complete(connect(event_loop, socket_path))
    client.init_glfw()
    client.poll_glfw_events()
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass

    client.stop()
    event_loop.stop()
    event_loop.run_forever()
    event_loop.close()


if __name__ == '__main__':
    log.configure('bel.glfw_client', logging.DEBUG)
    main()
