from bel.scene_node import SceneNode

class MeshNode(SceneNode):
    def __init__(self):
        self._verts = []
        self._faces = []

        self._draw_arrays = []
