from multiprocessing import Process
from socket import MSG_DONTWAIT, socketpair


MSG_LEN_FIELD_LEN = 8
RECV_CHUNK_SIZE = 1


class Receiver:
    def __init__(self, sock):
        self._sock = sock
        self._buf = bytearray()

    def recvall(self):
        try:
            self._ensure_min_buf_size(MSG_LEN_FIELD_LEN)
            len_field = self._take(MSG_LEN_FIELD_LEN)
            msg_len = int(len_field)
            self._ensure_min_buf_size(msg_len)
            return self._take(msg_len)
        except BlockingIOError:
            return None

    def _take(self, size):
        data = self._buf[:size]
        self._buf = self._buf[size:]
        return data

    def _ensure_min_buf_size(self, size):
        while len(self._buf) < size:
            self._buf += self._sock.recv(RECV_CHUNK_SIZE, MSG_DONTWAIT)


class WindowServer:
    def __init__(self, sock):
        self.conn = Receiver(sock)

        import cyglfw3 as glfw

        glfw.Init()
        window = glfw.CreateWindow(640, 480, 'bel.WindowServer')
        glfw.MakeContextCurrent(window)

        while not glfw.WindowShouldClose(window):
            glfw.SwapBuffers(window)
            glfw.PollEvents()
            msg = self.conn.recvall()
            if msg:
                print('received:', msg)



class WindowClient:
    def __init__(self):
        self.conn, server_conn = socketpair()
        self.proc = Process(target=WindowServer, args=(server_conn,))
        self.proc.start()

        self.sendall('hello there')

    def sendall(self, msg):
        len_fmt = '{:' + str(MSG_LEN_FIELD_LEN) + '}'
        len_field = len_fmt.format(len(msg))

        self.conn.sendall(len_field.encode())
        self.conn.sendall(msg.encode())
