#! /usr/bin/env python3

import logging

from bel import log
from bel.gldraw import DrawState
from bel.mesh import Mesh
from bel.mesh_node import MeshNode
from bel.scene import Scene
from bel.window import Window

class Demo:
    def __init__(self):
        self._scene = Scene()
        self._window = Window()
        self._window.on_draw = self.on_draw
        self._mesh = Mesh.load_obj('examples/cube.obj')
        self._scene.root.add_child(MeshNode(self._mesh))
        self._draw_state = DrawState()

    def on_draw(self):
        self._scene.draw(self._draw_state)
        self._draw_state.draw_all()

    def run(self):
        self._window.run()

def main():
    log.configure('demo', logging.DEBUG)

    demo = Demo()
    demo.run()


if __name__ == '__main__':
    main()
