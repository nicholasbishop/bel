# pylint: disable=missing-docstring

from unittest import TestCase

from numpy import allclose

from cgmath.vector import dot, magnitude, magnitude_squared, normalized, vec3

class TestVec3(TestCase):
    def test_create(self):
        self.assertTrue(allclose(vec3(), (0, 0, 0)))
        self.assertTrue(allclose(vec3(1, 2, 3), (1, 2, 3)))

    def test_dot(self):
        self.assertEqual(dot(vec3(3, 5, 7), vec3(2, 4, 6)), 68)

    def test_magnitude(self):
        vec = vec3(2, 4, 6)
        self.assertEqual(magnitude_squared(vec), 56)
        self.assertAlmostEqual(magnitude(vec), 7.483315)

    def test_normalized(self):
        self.assertTrue(allclose(normalized(vec3(0, 0, 4)), vec3(0, 0, 1)))
