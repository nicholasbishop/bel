import logging
from socket import AF_UNIX, MSG_DONTWAIT, SOCK_STREAM, socket

from bel.msg import Msg

MSG_LEN_FIELD_LEN = 8
RECV_CHUNK_SIZE = 4096


class ConnectionClosed(Exception):
    pass


# Custom & untested message protocol to ensure as many bugs as
# possible in the implementation. :)


class Conn:
    def __init__(self, sock):
        self._sock = sock
        self._recv_buf = bytearray()
        self._closed = False

    @classmethod
    def accept(cls, server_socket):
        logging.debug('waiting for client to connect...')
        sock, _ = server_socket.accept()
        logging.debug('connection accepted')
        return cls(sock)

    @classmethod
    def connect(cls, socket_path):
        logging.debug('creating client socket')
        sock = socket(AF_UNIX, SOCK_STREAM)
        logging.debug('connecting to socket %s', socket_path)
        sock.connect(socket_path)
        logging.debug('connected to socket %s', socket_path)
        return cls(sock)

    @property
    def socket(self):
        return self._sock

    def send_msg(self, msg):
        if self._closed:
            # TODO
            logging.debug('silently dropping message to closed connection')
            return

        raw_msg = msg.encode()

        len_fmt = '{:' + str(MSG_LEN_FIELD_LEN) + '}'
        len_field = len_fmt.format(len(raw_msg))

        self._sock.sendall(len_field.encode())
        self._sock.sendall(raw_msg)

    def read_messages_nonblocking(self):
        return self._read_messages(blocking=False)

    def read_messages_blocking(self):
        return self._read_messages(blocking=True)

    def _read_messages(self, blocking):
        try:
            # Read the length header. If blocking is False and not
            # enough bytes have been received yet this will raise
            # BlockingIOError.
            self._ensure_min_recv_buf_size(MSG_LEN_FIELD_LEN, blocking)
            msg_len = self._peek_msg_len()

            # Enough bytes have been received to know the size of the
            # next message, try to read the full message. Again may
            # raise BlockingIOError.
            self._ensure_min_recv_buf_size(MSG_LEN_FIELD_LEN + msg_len,
                                           blocking)

            # At this point we have *at least* one message to return,
            # but there may be more than one in the buffer. The caller
            # should receive all messages already in the buffer
            # because if the caller uses select() to sleep until the
            # next message is ready it would have no way of knowing
            # that additional messages are already ready.
            messages = [self._take_message(msg_len)]

            while len(self._recv_buf) > MSG_LEN_FIELD_LEN:
                msg_len = self._peek_msg_len()
                assert(msg_len is not None)
                if len(self._recv_buf) >= MSG_LEN_FIELD_LEN + msg_len:
                    messages.append(self._take_message(msg_len))

            return messages
        except BlockingIOError:
            return []

    def _peek(self, size):
        if len(self._recv_buf) >= size:
            return self._recv_buf[:size]
        else:
            return None

    def _peek_msg_len(self):
        len_field = self._peek(MSG_LEN_FIELD_LEN)
        if len_field is None:
            return None
        else:
            return int(len_field)

    def _take_message(self, msg_len):
        self._skip(MSG_LEN_FIELD_LEN)
        return Msg.decode(self._take(msg_len))

    def _take(self, size):
        data = self._recv_buf[:size]
        self._recv_buf = self._recv_buf[size:]
        return data

    def _skip(self, size):
        self._recv_buf = self._recv_buf[size:]

    def _raise_closed(self):
        self._closed = True
        raise ConnectionClosed()

    def _ensure_min_recv_buf_size(self, size, blocking):
        flags = 0 if blocking else MSG_DONTWAIT
        while len(self._recv_buf) < size:
            new_data = self._sock.recv(RECV_CHUNK_SIZE, flags)
            if len(new_data) == 0:
                self._raise_closed()
            self._recv_buf += new_data
