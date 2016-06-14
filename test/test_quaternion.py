# pylint: disable=missing-docstring

from unittest import TestCase

from numpy import allclose

from cgmath.quaternion import quat4f

class TestQuaternion(TestCase):
    def test_create(self):
        quat = quat4f(1, 2, 3, 4)
        self.assertTrue(allclose(quat.vector, (1, 2, 3)))
        self.assertEqual(quat.scalar, 4)
