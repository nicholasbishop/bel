import math

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


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

    @staticmethod
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

    @staticmethod
    def perspective(fov_y_degrees, size, near, far):
        """Create a new perspective matrix.

        fov_y_degrees: vertical field-of-view (in degrees)

        size: Vec2 size of the viewport

        near: near clipping distance

        far: far clipping distance

        Adapted from:
        nehe.gamedev.net/article/replacement_for_gluperspective/21002
        """
        aspect = size.x
        if size.y != 0:
            aspect /= size.y
        fh = math.tan((fov_y_degrees / 360.0) * math.pi) * near
        fw = fh * aspect
        return Mat4x4.frustum(-fw, fw, -fh, fh, near, far)


class Quat:
    def __init__(self):
        pass


class Transform:
    def __init__(self):
        self._translation = Vec3(0, 0, 0)
        self._scale = Vec3(1, 1, 1)
        self._rotation = Quat()

    def matrix(self):
        return Mat4x4.identity()
