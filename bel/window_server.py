import capnp

from bel import ipc_capnp as ipc


class WindowServer(ipc.Window.Server):
    def __init__(self):
        pass

    def sayHello(self, _context):
        return 'hello'
