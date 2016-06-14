# TODO
import numpy
from pyrr.matrix44 import create_perspective_projection_matrix

from bel.scene_node import SceneNode
from cgmath.vector import vec3

class CameraNode(SceneNode):
    def __init__(self):
        super().__init__()
        self._field_of_view_y = 90
        self._near = 0.01
        self._far = 100.0
        self._transform.loc = vec3(0, 0, -2)
        self._aspect_ratio = None
        self._projection_matrix = None

    @property
    def projection_matrix(self):
        return self._projection_matrix

    def update_projection_matrix(self, aspect_ratio):
        if self._aspect_ratio == aspect_ratio:
            return

        self._aspect_ratio = aspect_ratio
        # TODO
        pmat = create_perspective_projection_matrix(
            self._field_of_view_y,
            aspect_ratio,
            self._near,
            self._far)
        self._projection_matrix = numpy.array(pmat).reshape((4, 4))

    # TODO(nicholasbishop): this doesn't yet account for any parent
    # node transforms
    def view_matrix(self):
        return self._transform.matrix()

    def draw(self, draw_state):
        draw_state.update_matrix_uniform('projection',
                                         self._projection_matrix)
        draw_state.update_matrix_uniform('camera', self.view_matrix())
