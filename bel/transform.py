import math

from pyrr import Matrix44, Quaternion, Vector3

class Transform:
    def __init__(self):
        self._translation = Vector3()
        self._rotation = Quaternion()
        # TODO

    def matrix(self):
        return (Matrix44.from_translation(self._translation) *
                self._rotation.matrix44)

    def translate(self, vec):
        self._translation += vec

    def set_rotation(self, quat):
        self._rotation = quat

    def rotate(self, quat):
        self._rotation *= quat


def deg_to_rad(deg):
    return deg * math.pi / 180
