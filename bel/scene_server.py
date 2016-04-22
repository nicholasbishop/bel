import capnp

from bel import ipc_capnp as ipc
from bel.launcher import Launcher

class SceneServer(ipc.Scene.Server):
    def __init__(self):
        self._window = Launcher('bel.server', 'bel.window_server.WindowServer', ipc.Window)
        self._window.launch()

    def sayHello(self, _context):
        return "hello, i'm scene server"
