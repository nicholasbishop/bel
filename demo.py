#! /usr/bin/env python3

import logging

from cyglfw3.compatible import GLFW_KEY_ESCAPE

from bel import log
from bel.mesh import Mesh
from bel.mesh_node import MeshNode
from bel.scene import Scene
from bel.solids import cube_mesh
from bel.window import Window
from cgmath.vector import copy_xyz, vec3_from_scalar, vec3, vec4


class RayNode(MeshNode):
    def __init__(self):
        super().__init__()

        vi0 = self.mesh.add_vert()
        vi1 = self.mesh.add_vert()

        self.start = self.mesh.vert(vi0)
        self.end = self.mesh.vert(vi1)

        # Green to red
        self.start.col = vec4(0.0, 1.0, 0.0, 1.0)
        self.end.col = vec4(1.0, 0.0, 0.0, 1.0)

        self.mesh.add_edge(vi0, vi1)
        self._draw_edges = True


class Demo:
    def __init__(self):
        self._scene = Scene()
        self._window = Window(1600, 1200)

        self._window.on_draw = self.on_draw
        self._window.on_cursor_pos = self.on_cursor_pos
        self._window.on_key = self.on_key

        self._ray_node = self._scene.root.add_child(RayNode())

        self._mesh = Mesh.load_obj('examples/xyz-text.obj')
        self._scene.root.add_child(MeshNode(self._mesh))
        self._mouse_node = self._scene.root.add_child(
            MeshNode(cube_mesh()))
        self._mouse_node.transform.scale = vec3_from_scalar(0.1)

        # TODO
        self._scene.window_initialized(self._window.draw_state)

    def on_cursor_pos(self, loc):
        # TODO
        #copy_xy(self._mouse_node.transform.loc, loc)
        self._mouse_node._triangle_draw.needs_update = True

        ray = self._scene.ray_from_screen_coord(loc)
        ray.origin = vec3(0, 0, 1)
        # TODO
        self._ray_node.start.loc = ray.origin + ray.direction * 0.1
        self._ray_node.end.loc = ray.origin + ray.direction * 2
        self._ray_node._edge_buf.dirty = True

        #print(ray, self._ray_node.end.loc)
        #print(self._ray_node.start.loc, self._ray_node.end.loc)

        # TODO
        best_node, best_t = self._scene.ray_intersect(ray)
        if best_node is not None:
            copy_xyz(self._mouse_node.transform.loc,
                     ray.origin + ray.direction * best_t)
        else:
            print(None)
        #print(best_node, best_t)

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
