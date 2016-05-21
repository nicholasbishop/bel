import logging
import sys
from threading import Thread

from OpenGL import GL as gl
import capnp

from bel import ipc_capnp as ipc
from bel.server import run_server


class WindowServer(ipc.Window.Server):
    def __init__(self):
        self._scene = None

    def sayHello(self, _context):
        return 'hello'

    def setScene(self, scene):
        self._scene = scene

    def shutdown(self, _context):
        self._scene.shutdown().send()


def run_event_loop_and_server():
    run_server()


class Window:
    def __init__(self, glfw):
        self.glfw = glfw
        self.window = None

        # TODO
        socket_path = sys.argv[1]
        print(socket_path)
        client = capnp.TwoPartyClient(socket_path)
        self._window_server = client.bootstrap().cast_as(ipc.Window)

    def run(self):
        self.window = self.glfw.CreateWindow(640, 480, 'bel Window')
        self.glfw.MakeContextCurrent(self.window)

        # self.glfw.SetMouseButtonCallback(self.window, self.cb_mouse_button)
        # self.glfw.SetCursorPosCallback(self.window, self.cb_cursor_pos)

        while not self.glfw.WindowShouldClose(self.window):
            self.glfw.PollEvents()
            self.draw()

        self.send_shutdown()

    def draw(self):
        # TODO
        gl.glClearColor(0.3, 0.3, 0.4, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        width, height = self.glfw.GetFramebufferSize(self.window)
        gl.glViewport(0, 0, width, height)

        self.glfw.SwapBuffers(self.window)

    def send_shutdown(self):
        print('Window.send_shutdown')
        self._window_server.shutdown().send()


def run_glfw():
    logging.basicConfig(level=logging.INFO, format=
                        '%(levelname)s: window process '
                        '[%(filename)s:%(lineno)d] %(message)s')

    # pylint: disable=locally-disabled,no-member
    import cyglfw3 as glfw
    if not glfw.Init():
        raise RuntimeError('glfw.Init failed')

    glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = Window(glfw)
    window.run()


def main():
    print('here in window main')

    # TODO(nicholasbishop): explain this bit of magic
    capnp.remove_event_loop()
    capnp.create_event_loop(threaded=True)

    thread = Thread(target=run_event_loop_and_server)
    thread.start()

    # TODO(nicholasbishop): run glfw
    run_glfw()

    thread.join()


if __name__ == '__main__':
    main()
