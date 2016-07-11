#! /usr/bin/env python3

import logging

from cyglfw3.compatible import GLFW_KEY_ESCAPE

from bel import log
from bel.mesh import Mesh
from bel.mesh_node import MeshNode
from bel.scene import Scene
from bel.solids import cube_mesh
from bel.window import Window
from cgmath.vector import copy_xy, vec3_from_scalar

class Demo:
    def __init__(self):
        self._scene = Scene()
        self._window = Window(1600, 1200)

        self._window.on_draw = self.on_draw
        self._window.on_cursor_pos = self.on_cursor_pos
        self._window.on_key = self.on_key

        self._ray_node = self._scene.root.add_child(MeshNode())
        vi0 = self._ray_node.mesh.add_vert()
        vi1 = self._ray_node.mesh.add_vert()
        self._ray_start = self._ray_node.mesh.vert(vi0)
        self._ray_end = self._ray_node.mesh.vert(vi1)
        self._ray_node.mesh.add_edge(vi0, vi1)
        self._ray_node.draw_edges = True

        self._mesh = Mesh.load_obj('examples/xyz-text.obj')
        self._scene.root.add_child(MeshNode(self._mesh))
        self._mouse_node = self._scene.root.add_child(
            MeshNode(cube_mesh()))
        self._mouse_node.transform.scale = vec3_from_scalar(0.1)

        # TODO
        self._scene.window_initialized(self._window.draw_state)

    def on_cursor_pos(self, loc):
        # TODO
        transf = self._mouse_node.transform
        copy_xy(transf.loc, loc)
        ray = self._scene.ray_from_screen_coord(loc)
        self._ray_start.loc = ray.origin
        self._ray_end.loc = ray.origin + ray.direction * 1000
        # TODO
        self._ray_node._edge_buf.dirty = True
        self._mouse_node._triangle_draw.needs_update = True

    def on_key(self, key, scancode, action, mods):
        if key == GLFW_KEY_ESCAPE:
            self._window.close()

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
