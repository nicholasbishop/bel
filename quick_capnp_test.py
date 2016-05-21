#! /usr/bin/env python3

import atexit

import capnp

from bel import ipc_capnp as ipc
from bel.launcher import Launcher

launcher = Launcher('bel.server', 'bel.scene_server.SceneServer', ipc.Scene)
scene = launcher.launch()



scene.setClient(app)

# TODO
def event_loop(self):
    while True:
        pass
atexit.register(self.event_loop)
