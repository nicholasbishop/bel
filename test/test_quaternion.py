# pylint: disable=missing-docstring

from unittest import TestCase

from cgmath.quaternion import quat4f

class TestQuaternion(TestCase):
    def test_create(self):
        quat = quat4f(1, 2, 3, 4)
        self.assertEqual(quat.vector.as_tuple(), (1, 2, 3))
        self.assertEqual(quat.scalar, 4)
