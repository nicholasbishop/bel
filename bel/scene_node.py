from cgmath.affine import Transform

class SceneNode(object):
    def __init__(self):
        self._transform = Transform()
        self._children = []

    def add_child(self, child):
        self._children.append(child)
        return child

    @property
    def transform(self):
        return self._transform

    @property
    def children(self):
        return self._children

    def draw(self, draw_state):
        pass
