from mth import Vec3

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
    # TODO, worker thread
    def __init__(self):
        self._original_path = None
        self._verts = []
        self._faces = []

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
                    vec = Vec3()
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

        mesh = Mesh()
        mesh._original_path = path
        mesh._verts = verts
        mesh._faces = faces
        return mesh
