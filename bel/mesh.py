from cgmath.vector import vec3f

def _obj_remove_comment(line):
    ind = line.find('#')
    if ind != -1:
        line = line[:ind].rstrip()
    return line


class Vert:
    def __init__(self, loc):
        self.loc = loc


class Face:
    def __init__(self, indices):
        self.indices = indices


class Mesh:
    def __init__(self, verts, faces, path):
        self._original_path = path
        self._verts = verts
        self._faces = faces

    @property
    def verts(self):
        return self._verts

    @property
    def faces(self):
        return self._faces

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
