from unittest import TestCase

from cgmath.ray import Ray
from cgmath.ray_triangle_intersect import ray_triangle_intersect
from cgmath.vector import vec3

def xy_triangle():
    """Triangle in the XY plane."""
    return [vec3(0, 0, 2),
            vec3(2, 0, 2),
            vec3(1, 2, 2)]
    

class TestIntersect(TestCase):
    def test_intersect(self):
        # Ray pointing in the +Z direction
        ray = Ray(origin=vec3(1, 1, 0),
                  direction = vec3(0, 0, 1))

        triangle = xy_triangle()
        result = ray_triangle_intersect(ray, triangle)

        self.assertEqual(result, 2)
