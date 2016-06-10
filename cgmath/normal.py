def triangle_normal(v1, v2, v3):
    """Surface normal for the triangle (v1, v2, v3)."""
    e1 = v2 - v1
    e2 = v2 - v3
    return e1.cross(e2).normalized()
