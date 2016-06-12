from cgmath.vector import vec3f

def _obj_remove_comment(line):
    ind = line.find('#')
    if ind != -1:
        line = line[:ind].rstrip()
    return line


class Vert:
    def __init__(self, loc=None):
        self.loc = loc or vec3f(0, 0, 0)
        self.edge_indices = []


class Edge:
    def __init__(self, vi0, vi1, face_indices):
        self.vert_indices = (vi0, vi1)
        self.face_indices = face_indices

    def __eq__(self, other):
        return (self.vert_indices == other.vert_indices and
                self.face_indices == other.face_indices)

    def __repr__(self):
        return 'Edge({}, {})'.format(self.vert_indices[0],
                                     self.vert_indices[1])


class Face:
    def __init__(self, vert_indices):
        self.vert_indices = vert_indices

    def iter_vert_pairs(self):
        num_verts = len(self.vert_indices)
        for corner_index, vert_index in enumerate(self.vert_indices):
            next_corner_index = corner_index + 1
            if next_corner_index == num_verts:
                next_corner_index = 0

            next_vert_index = self.vert_indices[next_corner_index]
            yield (vert_index, next_vert_index)


class Mesh:
    def __init__(self, verts, faces, path=None):
        self._original_path = path
        self._verts = verts
        self._faces = faces
        self._edges = None
        self._update_edges()

    @property
    def verts(self):
        return self._verts

    @property
    def edges(self):
        assert self._edges != None
        return self._edges

    @property
    def faces(self):
        return self._faces

    def _update_edges(self):
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

    def vert(self, vert_index):
        return self._verts[vert_index]

    @classmethod
    def load_obj(cls, path):
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
                    vec = vec3f()
                    if len(parts) > 1:
                        vec.x = float(parts[1])
                    if len(parts) > 2:
                        vec.y = float(parts[2])
                    if len(parts) > 3:
                        vec.z = float(parts[3])
                    verts.append(Vert(vec))
                elif tok == 'f':
                    indices = [int(ind) - 1 for ind in parts[1:]]
                    faces.append(Face(indices))

        return Mesh(verts, faces, path)
