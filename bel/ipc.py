import atexit
import logging
import os
from socket import AF_UNIX, MSG_DONTWAIT, SOCK_STREAM, socket
import subprocess
import sys

import dill

MSG_LEN_FIELD_LEN = 8
RECV_CHUNK_SIZE = 4096


class ConnectionClosed(Exception):
    pass


class Conn:
    def __init__(self, sock):
        self._sock = sock
        self._recv_buf = bytearray()

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
            new_data = self._sock.recv(RECV_CHUNK_SIZE, flags)
            if len(new_data) == 0:
                raise ConnectionClosed()
            self._recv_buf += new_data
