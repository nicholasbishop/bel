from cgmath.affine import Transform

class SceneNode(object):
    def __init__(self):
        self._transform = Transform()
        self._children = []
