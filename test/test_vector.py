# pylint: disable=missing-docstring

from math import sqrt
from unittest import TestCase

from cgmath import vector as vec

class TestVec3(TestCase):
    def test_create(self):
        self.assertEqual(vec3f().as_tuple(), (0, 0, 0))
        self.assertEqual(vec3f(1, 2, 3).as_tuple(), (1, 2, 3))

    def test_dot(self):
        self.assertEqual(vec3f(3, 5, 7).dot(vec3f(2, 4, 6)), 68)

    def test_length_squared(self):
        self.assertEqual(vec3f(2, 4, 6).length_squared(), 56)

    def test_length(self):
        self.assertAlmostEqual(vec3f(2, 4, 6).length(), 7.483315)

    def test_normalized(self):
        self.assertEqual(vec3f(0, 0, 4).normalized().as_tuple(), (0, 0, 1))
