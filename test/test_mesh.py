from unittest import TestCase

from bel.mesh import Edge, Face, Mesh, Vert

def mesh_two_triangles_in_square():
    """
    v0___v3
     |\  |
     | \ |
     |__\|
    v1   v2
    """
    return Mesh(
        (
            Vert(), Vert(), Vert(), Vert(),
        ),
        (
            Face((0, 1, 2)),
            Face((0, 2, 3)),
        )
    )


class TestAdjacency(TestCase):
    def testEdges(self):
        mesh = mesh_two_triangles_in_square()

        expected_edges = [
            Edge(0, 1, [0]),
            Edge(1, 2, [0]),
            Edge(0, 2, [0, 1]),
            Edge(2, 3, [1]),
            Edge(0, 3, [1]),
        ]

        self.assertEqual(mesh.edges, expected_edges)

    def test_adj_vert_vert(self):
        mesh = mesh_two_triangles_in_square()

        self.assertEqual(set(mesh.adj_vert_vert(0)), set((1, 2, 3)))
        self.assertEqual(set(mesh.adj_vert_vert(1)), set((0, 2)))
        self.assertEqual(set(mesh.adj_vert_vert(2)), set((0, 1, 3)))
        self.assertEqual(set(mesh.adj_vert_vert(3)), set((0, 2)))
