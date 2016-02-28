from socket import MSG_DONTWAIT

import dill

MSG_LEN_FIELD_LEN = 8
RECV_CHUNK_SIZE = 4096

class Conn:
    def __init__(self, sock):
        self._sock = sock
        self._recv_buf = bytearray()

    def send_msg(self, data):
        msg = dill.dumps(data)

        len_fmt = '{:' + str(MSG_LEN_FIELD_LEN) + '}'
        len_field = len_fmt.format(len(msg))

        self._sock.sendall(len_field.encode())
        self._sock.sendall(msg)

    def read_msg_nonblocking(self):
        return self._read_msg(blocking=False)

    def read_msg_blocking(self):
        return self._read_msg(blocking=True)

    def _read_msg(self, blocking):
        try:
            self._ensure_min_recv_buf_size(MSG_LEN_FIELD_LEN, blocking)
            len_field = self._take(MSG_LEN_FIELD_LEN)
            msg_len = int(len_field)

            self._ensure_min_recv_buf_size(msg_len, blocking)
            return dill.loads(self._take(msg_len))
        except BlockingIOError:
            return None

    def _take(self, size):
        data = self._recv_buf[:size]
        self._recv_buf = self._recv_buf[size:]
        return data

    def _ensure_min_recv_buf_size(self, size, blocking):
        while len(self._recv_buf) < size:
            flags = 0 if blocking else MSG_DONTWAIT
            self._recv_buf += self._sock.recv(RECV_CHUNK_SIZE, flags)
