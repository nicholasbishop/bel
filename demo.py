#! /usr/bin/env python3

import logging

from bel import log
from bel.mesh import Mesh
from bel.mesh_node import MeshNode
from bel.scene import Scene
from bel.solids import cube_mesh
from bel.window import Window

class Demo:
    def __init__(self):
        self._scene = Scene()
        self._window = Window()

        self._window.on_draw = self.on_draw
        self._window.on_cursor_pos = self.on_cursor_pos

        self._mesh = Mesh.load_obj('examples/xyz-text.obj')
        self._scene.root.add_child(MeshNode(self._mesh))
        self._mouse_node = self._scene.root.add_child(
            MeshNode(cube_mesh()))

    def on_cursor_pos(self, loc):
        # TODO
        transf = self._mouse_node.transform
        transf.loc.x = loc.x
        transf.loc.y = -loc.y
        self._mouse_node._draw_cmd_dirty = True

    def on_draw(self):
        self._scene.draw(self._window.draw_state)

    def run(self):
        self._window.run()

def main():
    log.configure('demo', logging.DEBUG)

    demo = Demo()
    demo.run()


if __name__ == '__main__':
    main()
