#! /usr/bin/env python3

import logging

from cyglfw3.compatible import GLFW_KEY_ESCAPE

from bel import log
from bel.mesh import Mesh
from bel.mesh_node import MeshNode
from bel.scene import Scene
from bel.solids import cube_mesh
from bel.window import Window
from cgmath.vector import (copy_xyz, cross, normalized,
                           vec3_from_scalar, vec3, vec4)


class RayNode(MeshNode):
    def __init__(self):
        super().__init__()

        # Ray
        vi0 = self.mesh.add_vert()
        vi1 = self.mesh.add_vert()
        self.mesh.add_edge(vi0, vi1)

        # Cross 1
        vi2 = self.mesh.add_vert()
        vi3 = self.mesh.add_vert()
        self.mesh.add_edge(vi2, vi3)

        # Cross 2
        vi4 = self.mesh.add_vert()
        vi5 = self.mesh.add_vert()
        self.mesh.add_edge(vi4, vi5)

        self._v0 = self.mesh.vert(vi0)
        self._v1 = self.mesh.vert(vi1)

        self._v2 = self.mesh.vert(vi2)
        self._v3 = self.mesh.vert(vi3)

        self._v4 = self.mesh.vert(vi4)
        self._v5 = self.mesh.vert(vi5)

        self._v0.col = vec4(1, 0, 0)
        self._v1.col = self._v0.col.copy()

        self._v2.col = vec4(0, 1, 0)
        self._v3.col = self._v2.col.copy()

        self._v4.col = vec4(0, 0, 1)
        self._v5.col = self._v4.col.copy()

        self._draw_edges = True

    def update_ray(self, ray):
        up = vec3(0, 1, 0)
        cr1 = cross(ray.direction, up)
        cr2 = cross(cr1, ray.direction)

        # Visual length
        vlen = 0.01

        self._v0.loc = ray.origin
        self._v1.loc = ray.origin + ray.direction * vlen

        # Push cross away from actual origin
        push = 0.1
        org = ray.origin + ray.direction * push

        self._v2.loc = org
        self._v3.loc = org + cr1 * vlen

        self._v4.loc = org
        self._v5.loc = org + cr2 * vlen

        self._edge_buf.dirty = True


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
        self._mouse_node.transform.scale = vec3_from_scalar(0.02)
        self._mouse_node.pickable = False

        # TODO
        self._scene.window_initialized(self._window.draw_state)

    def on_cursor_pos(self, loc):
        ray = self._scene.ray_from_screen_coord(loc)
        self._ray_node.update_ray(ray)

        # TODO
        best_node, best_t = self._scene.ray_intersect(ray)
        if best_node is not None:
            hit = ray.origin + ray.direction * best_t
            mesh = best_node.mesh
            vert_index, _ = mesh.nearest_vert(hit)
            
            copy_xyz(self._mouse_node.transform.loc,
                     mesh.vert(vert_index).loc)
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
