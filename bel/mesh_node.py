from bel.scene_node import SceneNode

class MeshNode(SceneNode):
    def __init__(self, mesh):
        super().__init__()
        self._mesh = mesh

    def draw(self):
        pass
