import capnp

from bel import ipc_capnp as ipc
from bel.launcher import Launcher

class SceneServer(ipc.Scene.Server):
    def __init__(self):
        launcher = Launcher('bel.window_server',
                            'bel.window_server.WindowServer', ipc.Window)
        self._window = launcher.launch()
        self._client = None

    def sayHello(self, _context):
        return "hello, i'm scene server"

    def getApp(self, client, _context):
        self._client = client

    def shutdown(self, _context):
        self._client.shutdown().send()
