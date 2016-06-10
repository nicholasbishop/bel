from pyrr import Vector3

from bel.transform import Transform

class Camera:
    def __init__(self):
        self._transform = Transform()
        # TODO
        self._transform.translate(Vector3((0, 0, -2)))

    @property
    def transform(self):
        return self._transform
