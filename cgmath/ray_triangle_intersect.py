"""Ray-triangle intersection."""

# pylint: disable=invalid-name

from cgmath.vector import cross, dot

# TODO
EPSILON = 0.000001

# Adapted from:
# en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
def ray_triangle_intersect(ray, triangle):
    """Ray-triangle intersection.

    ray: cgmath.ray.Ray instance

    triangle: sequence of three points (cgmath.vector.vec3)

    Returns a scalar indicating the distance along the ray from the
    origin to the intersection. Returns None if no intersection found
    or multiple.
    """
    v1 = triangle[0]
    v2 = triangle[1]
    v3 = triangle[2]

    # Find vectors for two edges sharing v1
    e1 = v2 - v1
    e2 = v3 - v1

    # Begin calculating determinant - also used to calculate u
    # parameter
    P = cross(ray.direction, e2)

    # If determinant is near zero, ray lies in plane of triangle or
    # ray is parallel to plane of triangle
    det = dot(e1, P)

    # NOT CULLING
    if det > -EPSILON and det < EPSILON:
        return None
    inv_det = 1.0 / det

    # calculate distance from v1 to ray origin
    T = ray.origin - v1

    # Calculate u parameter and test bound
    u = dot(T, P) * inv_det
    # The intersection lies outside of the triangle
    if u < 0 or u > 1:
        return None

    # Prepare to test v parameter
    Q = cross(T, e1)

    # Calculate v parameter and test bound
    v = dot(ray.direction, Q) * inv_det
    # The intersection lies outside of the triangle
    if v < 0.0 or (u + v) > 1.0:
        return None


    t = dot(e2, Q) * inv_det

    if t > EPSILON: # ray intersection
        return t

    # No hit, no win
    return None
