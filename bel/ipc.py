import atexit
import os
from socket import AF_UNIX, MSG_DONTWAIT, SOCK_STREAM, socket
import subprocess
import sys

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



class LaunchProcess:
    def __init__(self, name, input_manager):
        # TODO!
        socket_path = '/tmp/{}.socket'.format(name)
        if os.path.exists(socket_path):
            os.remove(socket_path)
        server_sock = socket(AF_UNIX, SOCK_STREAM)
        server_sock.bind(socket_path)
        server_sock.listen(1)
        self._input_manager = input_manager

        cmd = []
        #cmd += ['gdb', '--eval-command', 'run', '--args']
        #cmd += ['apitrace', 'trace']
        #cmd += ['valgrind']
        #cmd += ['/home/nicholasbishop/vogl/vogl_build/vogl64', 'trace']
        cmd += ['venv/bin/python3',
                'bel/{}_process.py'.format(name),
                socket_path]

        env = dict(os.environ)
        env['PYTHONPATH'] = ':'.join(sys.path)

        #env['LIBGL_ALWAYS_SOFTWARE'] = '1'
        #env['MESA_DEBUG'] = '1'
        #env['LD_PRELOAD'] = '/home/nicholasbishop/vogl/vogl_build/libvogltrace64.so'

        self.proc = subprocess.Popen(cmd, env=env)

        sock, _ = server_sock.accept()
        self.conn = Conn(sock)
        atexit.register(self.event_loop)

    def event_loop(self):
        while True:
            msg = self.read_msg_blocking()
            self._input_manager.feed(msg)
            if msg['tag'] == 'exit':
                break
        self.proc.wait()

    def send_msg(self, msg):
        self.conn.send_msg(msg)

    def read_msg_blocking(self):
        return self.conn.read_msg_blocking()
