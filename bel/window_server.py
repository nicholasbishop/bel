import capnp

from bel import ipc_capnp as ipc


class WindowServer(ipc.Window.Server):
    def sayHello(self, _context):
        return 'hello'
