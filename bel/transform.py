from pyrr import Matrix44, Vector3

class Transform:
    def __init__(self):
        self._translation = Vector3()
        # TODO

    def matrix(self):
        return Matrix44.from_translation(self._translation)

    def translate(self, vec):
        self._translation += vec
