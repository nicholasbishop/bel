import atexit
import os
from socket import AF_UNIX, SOCK_STREAM, socket
import subprocess
import sys

from bel import ipc

class WindowClient:
    def __init__(self):
        # TODO!
        socket_path = "/tmp/bel.socket"
        if os.path.exists(socket_path):
            os.remove(socket_path)
        server_sock = socket(AF_UNIX, SOCK_STREAM)
        server_sock.bind(socket_path)
        server_sock.listen(1)

        cmd = []
        #cmd += ['gdb', '--eval-command', 'run', '--args']
        #cmd += ['apitrace', 'trace']
        #cmd += ['valgrind']
        #cmd += ['/home/nicholasbishop/vogl/vogl_build/vogl64', 'trace']
        cmd += ['venv/bin/python3', 'bel/window_process.py', socket_path]

        env = dict(os.environ)
        env['PYTHONPATH'] = ':'.join(sys.path)

        #env['LIBGL_ALWAYS_SOFTWARE'] = '1'
        #env['MESA_DEBUG'] = '1'
        #env['LD_PRELOAD'] = '/home/nicholasbishop/vogl/vogl_build/libvogltrace64.so'

        proc = subprocess.Popen(cmd, env=env)

        sock, _ = server_sock.accept()
        self.conn = ipc.Conn(sock)
        atexit.register(proc.wait)

    def send_msg(self, msg):
        self.conn.send_msg(msg)

    def read_msg_blocking(self):
        return self.conn.read_msg_blocking()
