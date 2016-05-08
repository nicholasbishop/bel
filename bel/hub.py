import logging
import os
from select import select
from socket import socket, AF_UNIX, SOCK_STREAM
from subprocess import Popen
import sys
from tempfile import TemporaryDirectory

from bel.ipc import Conn

def _create_socket(path):
    sock = socket(AF_UNIX, SOCK_STREAM)
    sock.bind(path)
    sock.listen(1)
    return sock


def copy_dict_entry(dst, src, key):
    if key in src:
        dst[key] = src[key]


class Child:
    SOCKET_PATH = object()

    def __init__(self, module_path):
        # TODO
        self._cmd = ['venv/bin/python3', module_path, self.SOCKET_PATH]

        env = dict(os.environ)
        self._env = {'PYTHONPATH': ':'.join(sys.path)}
        copy_dict_entry(self._env, env, 'DISPLAY')

        self._proc = None
        self._conn = None

    @property
    def conn(self):
        return self._conn

    @property
    def proc(self):
        return self._proc

    @classmethod
    def _finalize_command(cls, cmd, socket_path):
        for elem in cmd:
            if elem is cls.SOCKET_PATH:
                yield socket_path
            else:
                yield elem

    def launch(self, socket_path):
        if self._proc is not None:
            raise RuntimeError('process already launched')

        self._cmd = list(self._finalize_command(self._cmd, socket_path))
        logging.debug('launching child: %s', ' '.join(self._cmd))
        self._proc = Popen(self._cmd, env=self._env)

    def connect(self, server_sock):
        logging.debug('waiting for child to connect...')
        sock, _ = server_sock.accept()
        self._conn = Conn(sock)
        logging.debug('child connected')


class Hub:
    """Owner of all processes and IPC handles.

    The hub is a central broker for all IPC messaging. I don't think
    this is strictly necessary, but at least for getting things
    started it seems helpful to have a central place for launching
    processes and passing messages.
    """
    def __init__(self):
        self._scene_child = Child('bel/scene_process.py')
        self._window_child = Child('bel/window_process.py')
        self._children = (self._scene_child,
                          self._window_child)

    def launch_children(self):
        logging.debug('creating temporary directory')
        with TemporaryDirectory(prefix='bel-') as temp_dir:
            socket_path = os.path.join(temp_dir, 'bel.socket')
            logging.debug('creating socket: %s', socket_path)
            server_socket = _create_socket(socket_path)

            for child in self._children:
                child.launch(socket_path)

            for child in self._children:
                child.connect(server_socket)

    def _broadcast(self, msg):
        for child in self._children:
            child.conn.send_msg(msg)

    def run_until_exit(self):
        conns = dict(
            (child.conn.socket, child.conn) for child in self._children
        )
        in_rlist = conns.keys()
        in_wlist = []
        in_xlist = []
        running = True
        while running:
            out_rlist, _, _ = select(in_rlist, in_wlist, in_xlist)
            for sock in out_rlist:
                conn = conns[sock]
                msg = conn.read_msg_nonblocking()
                if msg['tag'] == 'exit':
                    running = False
                    break

        self._broadcast({'tag': 'exit'})
        for child in self._children:
            child.proc.wait()
