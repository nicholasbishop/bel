"""Simple but flexible Mesh data structure."""

from pqdict import minpq

from cgmath.vector import vec3

def _obj_remove_comment(line):
    """Strip "#" comment from a line."""
    ind = line.find('#')
    if ind != -1:
        line = line[:ind].rstrip()
    return line


class Vert:
    """Mesh vertex."""
    def __init__(self, loc=None):
        self.loc = vec3() if loc is None else loc
        self.edge_indices = []


class Edge:
    """Mesh edge."""
    def __init__(self, vi0, vi1, face_indices):
        self.vert_indices = (vi0, vi1)
        self.face_indices = face_indices

    def contains(self, vi0):
        """Return whether the edge's vertices include |vi0|."""
        return vi0 in self.vert_indices

    def other_vert_index(self, vi0):
        """Get the other vertex index in the edge.

        |vi0| must be one of the vertex indices in the edge.
        """
        assert vi0 in self.vert_indices
        if self.vert_indices[0] == vi0:
            return self.vert_indices[1]
        else:
            return self.vert_indices[0]

    def __eq__(self, other):
        return (self.vert_indices == other.vert_indices and
                self.face_indices == other.face_indices)

    def __repr__(self):
        return 'Edge({}, {})'.format(self.vert_indices[0],
                                     self.vert_indices[1])


class Face:
    """Mesh polygon."""
    def __init__(self, vert_indices):
        self.vert_indices = vert_indices

    def iter_vert_pairs(self):
        """Iterator of adjacent pairs of vertex indices.

        For example, a triangle with indices (2, 4, 6) will yield:
        (2, 4), (4, 6), (6, 2)
        """
        num_verts = len(self.vert_indices)
        for corner_index, vert_index in enumerate(self.vert_indices):
            next_corner_index = corner_index + 1
            if next_corner_index == num_verts:
                next_corner_index = 0

            next_vert_index = self.vert_indices[next_corner_index]
            yield (vert_index, next_vert_index)


class Mesh:
    """Simple but flexible Mesh data structure."""
    def __init__(self, verts, faces, path=None):
        self._original_path = path
        self._verts = verts
        self._faces = faces
        self._edges = None
        self._update_edges()

    @property
    def verts(self):
        """Mesh vertices."""
        return self._verts

    @property
    def edges(self):
        """Mesh edges."""
        assert self._edges != None
        return self._edges

    @property
    def faces(self):
        """Mesh faces."""
        return self._faces

    def vert(self, vert_index):
        """Get the |Vert| at |vertex_index|."""
        return self._verts[vert_index]

    def edge(self, edge_index):
        """Get the |Edge| at |edge_index|."""
        return self._edges[edge_index]

    def edge_index_between(self, vi0, vi1):
        """Get the edge index between |vi0| and |vi1|.

        Returns None if no such edge is found."""
        for ei0 in self.vert(vi0).edge_indices:
            edge = self.edge(ei0)
            if edge.contains(vi1):
                return ei0
        return None

    def edge_between(self, vi0, vi1):
        return self.edge(self.edge_index_between(vi0, vi1))

    def adj_vert_edge(self, vi0):
        """Edges adjacent to the vertex |vi0|."""
        for ei0 in self.vert(vi0).edge_indices:
            yield self.edge(ei0)

    def adj_vert_vert(self, vi0):
        """Vertex indices adjacent to the vertex |vi0|."""
        for edge in self.adj_vert_edge(vi0):
            yield edge.other_vert_index(vi0)

    def edge_verts(self, edge):
        """Get the pair of |Vert|s in the edge."""
        return (self.vert(edge.vert_indices[0]),
                self.vert(edge.vert_indices[1]))

    def edge_length(self, edge):
        """Get the distance between the edge's vertices."""
        pair = self.edge_verts(edge)
        return pair[0].loc.distance(pair[1].loc)

    def nearest_vert(self, loc):
        """Get the index of the vertex closest to |loc|.

        Returns a pair of (vertex_index, distance_squared)

        TODO(nicholasbishop): use a spatial hierarchy to make this
        faster.
        """
        best_vert_index = None
        best_dist_squared = float('inf')
        for index, vert in enumerate(self._verts):
            dist_squared = loc.distance_squared(vert.loc)
            if dist_squared < best_dist_squared:
                best_vert_index = index
                best_dist_squared = dist_squared
        return (best_vert_index, best_dist_squared)

    class DijkstraResult:
        """A list of |DijkstraResult| is returned by |dijkstra|."""
        def __init__(self, dist=float('inf'), prev=None):
            self.dist = dist
            self.prev = prev

        def __eq__(self, other):
            return self.dist == other.dist and self.prev == other.prev

        def __repr__(self):
            return 'DijkstraResult(dist={}, prev={})'.format(self.dist,
                                                             self.prev)

    def dijkstra(self, vi0, distance):
        """Calculate shortest path from |vi0| to all other verts.

        distance: callable that takes two adjacent vertex indices and
                  returns a number indicating the distance between
                  them.

        Returns a list of |DijkstraResult|.

        Adapted from:
        http://pqdict.readthedocs.io/en/latest/examples.html

        """
        result = []

        queue = minpq()
        for vi1 in range(len(self._verts)):
            queue[vi1] = float('inf')
            result.append(self.DijkstraResult())
        queue[vi0] = 0

        for vi2, min_dist in queue.popitems():
            result[vi2].dist = min_dist

            for vi3 in self.adj_vert_vert(vi2):
                if vi3 in queue:
                    new_score = result[vi2].dist + distance(vi2, vi3)
                    if new_score < queue[vi3]:
                        # pqdict update is O(log n)
                        queue[vi3] = new_score
                        result[vi3].prev = vi2

        return result

    def _update_edges(self):
        """Recalculate edge adjacency.

        TODO(nicholasbishop): this doesn't correctly handle repeated
        calls because face/vert adjacency lists aren't cleared first.
        """
        self._edges = []
        for face_index, face in enumerate(self._faces):
            for vi0, vi1 in face.iter_vert_pairs():
                assert vi0 != vi1
                vi0, vi1 = sorted((vi0, vi1))

                edge_indices = self.vert(vi0).edge_indices

                found = False
                edge = None
                for ei0 in edge_indices:
                    edge = self._edges[ei0]
                    if edge.vert_indices == (vi0, vi1):
                        found = True
                        break

                if found:
                    edge.face_indices.append(face_index)
                else:
                    ei1 = len(self._edges)
                    self.vert(vi0).edge_indices.append(ei1)
                    self.vert(vi1).edge_indices.append(ei1)
                    self._edges.append(Edge(vi0, vi1, [face_index]))

    @classmethod
    def load_obj(cls, path):
        """Create a |Mesh| from an obj file."""
        with open(path) as rfile:
            verts = []
            faces = []
            for line in rfile.readlines():
                line = _obj_remove_comment(line)
                parts = line.split()
                if len(parts) == 0:
                    continue
                tok = parts[0]
                if tok == 'v':
                    vec = vec3()
                    if len(parts) > 1:
                        vec[0] = float(parts[1])
                    if len(parts) > 2:
                        vec[1] = float(parts[2])
                    if len(parts) > 3:
                        vec[2] = float(parts[3])
                    verts.append(Vert(vec))
                elif tok == 'f':
                    indices = [int(ind) - 1 for ind in parts[1:]]
                    faces.append(Face(indices))

        return Mesh(verts, faces, path)
