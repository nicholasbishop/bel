import numpy
from pyrr import Matrix44, Quaternion, Vector3, Vector4, vector
from pyrr.vector3 import generate_normals

from bel.auto_name import auto_name
from bel.msg import Msg, Tag

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
        self._vert_buf_uid = auto_name('vertbuf')
        self._draw_cmd_uid = auto_name('drawcmd')

    def create_draw_array(self):
        elem_per_vert = 6
        vert_per_tri = 3
        fac = elem_per_vert * vert_per_tri

        num_triangles = 0
        for face in self._faces:
            num_triangles += len(face.indices) - 2

        verts = numpy.empty(num_triangles * fac, numpy.float32)
        out = 0

        for face in self._faces:
            vi0 = face.indices[-1]
            for i in range(len(face.indices) - 2):
                vi1 = face.indices[i]
                vi2 = face.indices[i + 1]

                locs = [self._verts[vit].loc for vit in (vi0, vi1, vi2)]
                nor = Vector3(generate_normals(*locs))

                for loc in locs:
                    verts[out + 0] = loc.x
                    verts[out + 1] = loc.y
                    verts[out + 2] = loc.z
                    verts[out + 3] = nor.x
                    verts[out + 4] = nor.y
                    verts[out + 5] = nor.z
                    out += 6
        return verts

    # TODO, name
    def send_draw_stuff(self, conn):
        vert_nors = self.create_draw_array()
        num_triangles = len(vert_nors) // 6
        bytes_per_float32 = 4

        conn.send_msg(Msg(Tag.WND_UpdateBuffer, {
            'uid': self._vert_buf_uid,
            'array': vert_nors
        }))
        conn.send_msg(Msg(Tag.WND_UpdateDrawCommand, {
            'uid': self._draw_cmd_uid,
            'material': 'default',
            'attributes': {
                'vert_loc': {
                    'buffer': self._vert_buf_uid,
                    'components': 3,
                    'gltype': 'float',
                    'normalized': False,
                    'offset': 0,
                    'stride': bytes_per_float32 * 6
                },
                'vert_nor': {
                    'buffer': self._vert_buf_uid,
                    'components': 3,
                    'gltype': 'float',
                    'normalized': False,
                    'offset': bytes_per_float32 * 3,
                    'stride': bytes_per_float32 * 6
                }
            },
            # 'uniforms': {
            #     'model_view':
            #     MatrixUniform(self._transform.matrix())
            # },
            'range': (0, num_triangles),
            'primitive': 'triangles'
        }))

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
                    vec = Vector3()
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
