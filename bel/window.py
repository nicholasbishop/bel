import logging
from multiprocessing import Process
from socket import socketpair

from OpenGL import GL as gl

from bel import ipc

class WindowServer:
    def __init__(self, sock):
        logging.basicConfig(level=logging.DEBUG, format=
                            '%(levelname)s: window process '
                            '[%(filename)s:%(lineno)d] %(message)s')

        self.conn = ipc.Conn(sock)
        self.command_buffer = None

        import cyglfw3 as glfw

        if not glfw.Init():
            raise RuntimeError('glfw.Init failed')

        window = glfw.CreateWindow(640, 480, 'bel.WindowServer')
        glfw.MakeContextCurrent(window)

        while not glfw.WindowShouldClose(window):
            self.draw()

            glfw.SwapBuffers(window)
            glfw.PollEvents()
            msg = self.conn.read_msg_nonblocking()
            if msg is not None:
                if hasattr(msg, 'draw'):
                    self.command_buffer = msg
                else:
                    gl.glCreateProgram()
                    ret = msg()
                    self.conn.send_msg(ret)


    def draw(self):
        if self.command_buffer is not None:
            self.command_buffer.draw()


class WindowClient:
    def __init__(self):
        # TODO(nicholasbishop): verify that the defaults for
        # socketpair guarantee message ordering
        sock, server_sock = socketpair()
        self.conn = ipc.Conn(sock)
        self.proc = Process(target=WindowServer, args=(server_sock,))
        self.proc.start()

    def send_msg(self, msg):
        self.conn.send_msg(msg)

    def read_msg_blocking(self):
        return self.conn.read_msg_blocking()
