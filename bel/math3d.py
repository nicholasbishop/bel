import math

import numpy

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


def flatten(src):
    while hasattr(src, '__len__') and len(src) > 0:
        first = src[0]
        if isinstance(first, tuple) or isinstance(first, list):
            src = first
        else:
            return src
    return src


class Vec3:
    def __init__(self, *args):
        args = flatten(args)
        if len(args) > 0 and isinstance(args[0], Vec3):
            args = [args[0].x,
                    args[0].y,
                    args[0].z]
        num = len(args)
        self.x = args[0] if num > 0 else 0
        self.y = args[1] if num > 1 else 0
        self.z = args[2] if num > 2 else 0

    def __repr__(self):
        return 'vec({}, {}, {})'.format(
            self.x, self.y, self.z)


class Mat4x4:
    def __init__(self, *array):
        if len(array) == 0:
            array = [0] * 16

        self._dat = numpy.matrix((array[0:4],
                                  array[4:8],
                                  array[8:12],
                                  array[12:16]))

    def __mul__(self, other):
        mat = Mat4x4()
        mat._dat = self._dat * other._dat
        return mat

    def __str__(self):
        return str(self._dat)

    @staticmethod
    def identity():
        return Mat4x4(1, 0, 0, 0,
                      0, 1, 0, 0,
                      0, 0, 1, 0,
                      0, 0, 0, 1)

    @staticmethod
    def scale(x, y, z):
        return Mat4x4(x, 0, 0, 0,
                      0, y, 0, 0,
                      0, 0, z, 0,
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

    @staticmethod
    def translate(*vec):
        vec = Vec3(vec)
        #print(vec)
        return Mat4x4(1, 0, 0, vec.x,
                      0, 1, 0, vec.y,
                      0, 0, 1, vec.z,
                      0, 0, 0, 1)


class Quat:
    def __init__(self, x=0, y=0, z=0, w=0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    @staticmethod
    def from_axis_angle(axis, angle):
        half_angle = angle * 0.5
        fac = math.sin(half_angle)
        self.x = axis.x * fac
        self.y = axis.y * fac
        self.z = axis.z * fac
        self.w = math.cos(half_angle)


class Transform:
    def __init__(self):
        self._translation = Vec3(0, 0, 0)
        self._scale = Vec3(1, 1, 1)
        self._rotation = Quat()

    def set_scale(self, x, y, z):
        self._scale = Vec3(x, y, z)

    def set_translation(self, *vec):
        self._translation = Vec3(vec)

    def matrix(self):
        return (Mat4x4.translate(self._translation) *
                Mat4x4.scale(self._scale.x,
                             self._scale.y,
                             self._scale.z))
