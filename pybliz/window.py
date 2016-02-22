import capnp
from pybliz import pybliz_capnp

class Window:
    def __init__(self):
        address = 'localhost:3333'

        class Server(pybliz_capnp.Gpu.Server):
            pass

        server = capnp.TwoPartyServer(address, bootstrap=Server)
        server.run_forever()
        pass
