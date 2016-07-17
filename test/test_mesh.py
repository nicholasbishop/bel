# pylint: disable=missing-docstring

from unittest import TestCase

from bel.mesh import Edge, Face, Mesh, Vert
from cgmath.vector import vec3

def mesh_two_adj_triangles():
    r"""
    v0______v3
     |\    /
     | \  /
     |__\/
    v1   v2
    """
    return Mesh(
        (
            Vert(vec3(0, 0, 0)),
            Vert(vec3(0, 1, 0)),
            Vert(vec3(1, 1, 0)),
            Vert(vec3(2, 0, 0)),
        ),
        (
            Face((0, 1, 2)),
            Face((0, 2, 3)),
        )
    )


class TestTriangleFan(TestCase):
    def test_degenerate(self):
        face = Face((2,))
        fan = list(face.iter_triangle_fan())
        self.assertEqual(fan, [])

        face = Face((2, 4))
        fan = list(face.iter_triangle_fan())
        self.assertEqual(fan, [])

    def test_triangle(self):
        face = Face((2, 4, 6))
        fan = list(face.iter_triangle_fan())
        self.assertEqual(fan, [(2, 4, 6)])

    def test_quad(self):
        face = Face((2, 4, 6, 8))
        fan = list(face.iter_triangle_fan())
        self.assertEqual(fan, [(2, 4, 6), (2, 6, 8)])


class TestAdjacency(TestCase):
    def test_edges(self):
        mesh = mesh_two_adj_triangles()

        expected_edges = [
            Edge(0, 1, [0]),
            Edge(1, 2, [0]),
            Edge(0, 2, [0, 1]),
            Edge(2, 3, [1]),
            Edge(0, 3, [1]),
        ]

        self.assertEqual(mesh.edges, expected_edges)

    def test_adj_vert_vert(self):
        mesh = mesh_two_adj_triangles()

        self.assertEqual(set(mesh.adj_vert_vert(0)), set((1, 2, 3)))
        self.assertEqual(set(mesh.adj_vert_vert(1)), set((0, 2)))
        self.assertEqual(set(mesh.adj_vert_vert(2)), set((0, 1, 3)))
        self.assertEqual(set(mesh.adj_vert_vert(3)), set((0, 2)))


class TestMeasurement(TestCase):
    def test_edge_length(self):
        mesh = mesh_two_adj_triangles()

        edge = mesh.edge_between(0, 1)
        self.assertEqual(mesh.edge_length(edge), 1)

        edge = mesh.edge_between(0, 3)
        self.assertEqual(mesh.edge_length(edge), 2)


class TestDijkstra(TestCase):
    def test_dijkstra_const(self):
        cls = Mesh.DijkstraResult
        mesh = mesh_two_adj_triangles()

        # Constant edge weight
        def cb_dist(vi0, vi1):
            return 1

        result = mesh.dijkstra(0, cb_dist)
        self.assertEqual(result, [
            cls(0, None),
            cls(1, 0),
            cls(1, 0),
            cls(1, 0),
        ])

        result = mesh.dijkstra(1, cb_dist)
        self.assertEqual(result[:3], [
            cls(1, 1),
            cls(0, None),
            cls(1, 1),
        ])
        self.assertEqual(result[3].dist, 2)
        self.assertIn(result[3].prev, (0, 2))
