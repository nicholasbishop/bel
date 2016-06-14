from cgmath.vector import cross, normalized

def triangle_normal(v1, v2, v3):
    """Surface normal for the triangle (v1, v2, v3)."""
    e1 = v2 - v3
    e2 = v2 - v1
    return normalized(cross(e1, e2))
