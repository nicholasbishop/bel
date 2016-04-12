#! /usr/bin/env python3

import capnp

from bel import ipc_capnp as ipc

def restorer(ref_id):
    print(ref_id)

from bel.launcher import Launcher

launcher = Launcher('bel.window_server.WindowServer', ipc.Window)
launcher.launch()

"""
So it looks something like this:

Demo creates a "Scene" object. This Scene object could be fully
spelled out as a SceneClient. The SceneClient launches a new
process. That process starts a server on some port or path passed in
as a command-line argument. Meanwhile the SceneClient waits until it
can connect a capnp client to the server. Once it does, the Demo can
continue on to doing interesting things like RPC calls to the Scene
(via the SceneClient). 


"""
