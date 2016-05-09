import logging
import os
from select import select
from socket import socket, AF_UNIX, SOCK_STREAM
from subprocess import Popen
import sys
from tempfile import TemporaryDirectory
from threading import Thread

from bel.ipc import Conn, ConnectionClosed
from bel.msg import Msg, Tag

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
        self._conn = Conn.accept(server_sock)


class Hub:
    """Owner of all processes and IPC handles.

    The hub is a central broker for all IPC messaging. I don't think
    this is strictly necessary, but at least for getting things
    started it seems helpful to have a central place for launching
    processes and passing messages.

    TODO(nicholasbishop): split the two threads apart more, confusing
    currently.
    """
    def __init__(self):
        self._scene_child = Child('bel/scene_process.py')
        self._window_child = Child('bel/window_process.py')
        self._children = (self._scene_child,
                          self._window_child)
        self._bg_thread = Thread(name='bel.hub.Hub',
                                 target=self._bg_thread_target)
        self._thread_server_conn = None
        self._thread_client_conn = None

        # TODO: make easier to ensure cleanup
        logging.debug('creating temporary directory')
        self._temp_dir = TemporaryDirectory(prefix='bel-')
        self._socket_path = os.path.join(self._temp_dir.name, 'bel.socket')
        self._server_socket = None
        self._create_server_socket()

    def _delete_socket_directory(self):
        self._temp_dir.cleanup()

    def start_background_thread(self):
        self._bg_thread.start()
        self._thread_client_conn = Conn.connect(self._socket_path)

    def join_background_thread(self):
        self._bg_thread.join()
        self._delete_socket_directory()

    # TODO: target?
    def send_msg(self, msg):
        self._thread_client_conn.send_msg(msg)

    def _bg_thread_target(self):
        self._launch_children()
        self._run_until_exit()

    def _create_server_socket(self):
        logging.debug('creating socket: %s', self._socket_path)
        self._server_socket = _create_socket(self._socket_path)

    def _launch_children(self):
        self._thread_server_conn = Conn.accept(self._server_socket)

        for child in self._children:
            child.launch(self._socket_path)
            child.connect(self._server_socket)

    def _broadcast(self, msg):
        for child in self._children:
            child.conn.send_msg(msg)

    def _cleanup(self):
        self._broadcast(Msg(Tag.Exit))
        for child in self._children:
            child.proc.wait()

    def _run_until_exit(self):
        conns = dict(
            (child.conn.socket, child.conn) for child in self._children
        )
        conns[self._thread_server_conn.socket] = self._thread_server_conn
        in_rlist = list(conns.keys())
        in_wlist = []
        in_xlist = []
        running = True
        while running:
            out_rlist, _, _ = select(in_rlist, in_wlist, in_xlist)
            for sock in out_rlist:
                conn = conns[sock]
                try:
                    msg = conn.read_msg_nonblocking()
                    if msg.tag == Tag.Exit:
                        running = False
                        break
                    # TODO
                    elif msg.tag.name.startswith('SCE_'):
                        logging.debug('sending sce msg: %r', msg.tag)
                        self._scene_child.conn.send_msg(msg)
                    elif msg.tag.name.startswith('WND_'):
                        logging.debug('sending wnd msg: %r', msg.tag)
                        self._window_child.conn.send_msg(msg)
                    else:
                        raise ValueError('invalid tag', msg.tag)
                except ConnectionClosed:
                    in_rlist.remove(sock)
                    # TODO
                    logging.error('connection closed')

        self._cleanup()
