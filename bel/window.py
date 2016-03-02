import logging
from multiprocessing import Process
from socket import socketpair

from OpenGL import GL as gl

from bel import ipc

class WindowServer:
    def __init__(self, sock, glfw):
        self.conn = ipc.Conn(sock)
        self.command_buffer = None
        self.glfw = glfw
        self.materials = {}

    def run(self):
        window = self.glfw.CreateWindow(640, 480, 'bel.WindowServer')
        self.glfw.MakeContextCurrent(window)

        while not self.glfw.WindowShouldClose(window):
            self.draw()

            self.glfw.SwapBuffers(window)
            self.glfw.PollEvents()
            msg = self.conn.read_msg_nonblocking()
            if msg is not None:
                if hasattr(msg, 'draw'):
                    self.command_buffer = msg
                else:
                    msg(self.materials)
                    # ret = msg()
                    # self.conn.send_msg(ret)


    def draw(self):
        if self.command_buffer is not None:
            self.command_buffer.draw(self.materials)


def window_server_main(server_sock):
    logging.basicConfig(level=logging.DEBUG, format=
                        '%(levelname)s: window process '
                        '[%(filename)s:%(lineno)d] %(message)s')

    # pylint: disable=locally-disabled,no-member
    import cyglfw3 as glfw
    if not glfw.Init():
        raise RuntimeError('glfw.Init failed')

    window = WindowServer(server_sock, glfw)
    window.run()


class WindowClient:
    def __init__(self):
        # TODO(nicholasbishop): verify that the defaults for
        # socketpair guarantee message ordering
        sock, server_sock = socketpair()
        self.conn = ipc.Conn(sock)
        self.proc = Process(target=window_server_main, args=(server_sock,))
        self.proc.start()

    def send_msg(self, msg):
        self.conn.send_msg(msg)

    def read_msg_blocking(self):
        return self.conn.read_msg_blocking()
