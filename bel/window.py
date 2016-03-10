import logging
import os
from socket import AF_UNIX, SOCK_STREAM, socket
import subprocess

from OpenGL import GL as gl

from bel import ipc
from bel.shader import ShaderProgram
from bel.buffer_object import ArrayBufferObject
import sys
class WindowClient:
    def __init__(self):
        # TODO!
        socket_path = "/tmp/bel.socket"
        if os.path.exists(socket_path):
            os.remove(socket_path)
        server_sock = socket(AF_UNIX, SOCK_STREAM)
        server_sock.bind(socket_path)
        server_sock.listen(1)
        # tracelib = '/home/nicholasbishop/apitrace/build/wrappers/glxtrace.so'
        # os.environ['LD_PRELOAD'] = tracelib
        cmd = []
        cmd += ['apitrace', 'trace']
        cmd += ['venv/bin/python3', 'bel/window_process.py', socket_path]
        env = dict(os.environ)
        env['PYTHONPATH'] = ':'.join(sys.path)
        #proc = subprocess.Popen(cmd, stdin=server_sock.fileno(), env=env)
        proc = subprocess.Popen(cmd, env=env)
        sock, _ = server_sock.accept()
        self.conn = ipc.Conn(sock)
        import time
        print(proc)
        import atexit
        atexit.register(lambda: proc.wait())
        #time.sleep(10)
        #self.proc = Process(target=window_server_main, args=(server_sock,))
        #self.proc.start()

    def send_msg(self, msg):
        self.conn.send_msg(msg)

    def read_msg_blocking(self):
        return self.conn.read_msg_blocking()
