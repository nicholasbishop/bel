from unittest import TestCase

from bel.mesh import Edge, Face, Mesh, Vert

class TestMesh(TestCase):
    def testEdges(self):
        """
        v0___v3
         |\  |
         | \ |
         |__\|
        v1   v2
        """
        mesh = Mesh(
            (
                Vert(), Vert(), Vert(), Vert(),
            ),
            (
                Face((0, 1, 2)),
                Face((0, 2, 3)),
            )
        )

        expected_edges = [
            Edge(0, 1, [0]),
            Edge(1, 2, [0]),
            Edge(0, 2, [0, 1]),
            Edge(2, 3, [1]),
            Edge(0, 3, [1]),
        ]

        self.assertEqual(mesh.edges, expected_edges)
