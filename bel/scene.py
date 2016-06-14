from numpy import dot

from bel.camera_node import CameraNode
from bel.scene_node import SceneNode

from cgmath.vector import normalized, vec4_from_vec2, vec3_from_vec4
from cgmath.matrix import inverse

class Scene(object):
    def __init__(self):
        self._root = SceneNode()
        self._camera = self._root.add_child(CameraNode())

    @property
    def root(self):
        return self._root

    def window_initialized(self, window_state):
        self._camera.update_projection_matrix(window_state.aspect_ratio())

    def iter_nodes(self):
        stack = [self._root]
        while len(stack) != 0:
            node = stack.pop()
            stack += node.children
            yield node

    def draw(self, draw_state):
        for node in self.iter_nodes():
            node.draw(draw_state)

    def ray_from_screen_coord(self, screen_loc):
        # Adapted from http://antongerdelan.net/opengl/raycasting.html
        cam = self._camera
        ray_clip = vec4_from_vec2(screen_loc, -1, 1);
        ray_eye = inverse(cam.projection_matrix).dot(ray_clip)
        ray_eye = vec4_from_vec2(ray_eye, -1.0, 0.0)
        ray_wor = vec3_from_vec4(inverse(cam.view_matrix()) * ray_eye)
        ray_wor = normalized(ray_wor)
        return ray_wor
