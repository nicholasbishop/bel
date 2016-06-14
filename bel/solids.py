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

        # TODO(nicholasbishop): add the side faces
    ]
    return Mesh(verts, faces)
