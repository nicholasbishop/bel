#! /usr/bin/env python3

import capnp

from bel import ipc_capnp as ipc
from bel.launcher import Launcher

launcher = Launcher('bel.server', 'bel.scene_server.SceneServer', ipc.Scene)
launcher.launch()
