# pylint: disable=missing-docstring

from unittest import TestCase

from numpy import allclose

from cgmath.matrix import mat4, mat4_look_at
from cgmath.vector import vec3

class TestMat4(TestCase):
    def test_look_at(self):
        actual = mat4_look_at(eye=vec3(0, 0, 2),
                              target=vec3(0, 0, 0),
                              up=vec3(0, 1, 0))
        expected = mat4(
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, -2,
            0, 0, 0, 1
        )
        self.assertTrue(allclose(actual, expected))
