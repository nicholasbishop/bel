from bel.camera_node import CameraNode
from bel.scene_node import SceneNode

class Scene(object):
    def __init__(self):
        self._root = SceneNode()
        self._camera = self._root.add_child(CameraNode())

    @property
    def root(self):
        return self._root

    def iter_nodes(self):
        stack = [self._root]
        while len(stack) != 0:
            node = stack.pop()
            stack += node.children
            yield node

    def draw(self, draw_state):
        for node in self.iter_nodes():
            node.draw(draw_state)
