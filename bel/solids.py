from bel.mesh import Face, Mesh, Vert
from cgmath.vector import vec3

def cube_mesh():
    verts = [
        Vert(vec3(-1, -1, -1)),
        Vert(vec3(-1, +1, -1)),
        Vert(vec3(+1, +1, -1)),
        Vert(vec3(+1, -1, -1)),

        Vert(vec3(-1, -1, +1)),
        Vert(vec3(-1, +1, +1)),
        Vert(vec3(+1, +1, +1)),
        Vert(vec3(+1, -1, +1)),
    ]
    faces = [
        Face([0, 1, 2, 3]),
        Face([7, 6, 5, 4]),

        Face([0, 4, 5, 1]),
        Face([2, 3, 7, 6]),

        Face([1, 5, 6, 2]),
        Face([0, 3, 7, 4]),
    ]
    return Mesh(verts, faces)
