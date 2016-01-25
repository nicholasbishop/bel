class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z


class Mat4x4:
    def __init__(self, *array):
        self._array = array

    @staticmethod
    def identity():
        return Mat4x4(1, 0, 0, 0,
                      0, 1, 0, 0,
                      0, 0, 1, 0,
                      0, 0, 0, 1)

    def frustum(right, left, top, bottom, near, far):
        rml = right - left
        rpl = right + left
        tmb = top - bottom
        tpb = top + bottom
        fmn = far - near
        fpn = far + near
        n2 = near * 2
        n2f = n2 * far
        
        return Mat4x4(n2 / rml, 0,         rpl / rml,  0,
                      0,        n2 / tmb,  tpb / tmb,  0,
                      0,        0,        -fpn / fmn, -n2f / fmn,
                      0,        0,        -1,          0)


class Quat:
    def __init__(self):
        pass


class Transform:
    def __init__(self):
        self._translation = Vec3(0, 0, 0)
        self._scale = Vec3(1, 1, 1)
        self._rotation = Quat()
