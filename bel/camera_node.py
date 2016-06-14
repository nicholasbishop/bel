from bel.scene_node import SceneNode

from cgmath.vector import vec3

class CameraNode(SceneNode):
    def __init__(self):
        super().__init__()
        # TODO
        self._transform.loc = vec3(0, 0, -2)

    def draw(self, draw_state):
        draw_state.update_matrix_uniform(
            'camera', self._transform.matrix())
