import numpy

from bel.auto_name import auto_name
from bel.scene_node import SceneNode

class MeshNode(SceneNode):
    def __init__(self, mesh):
        super().__init__()
        self._mesh = mesh
        self._view_needs_update = True
        self._vert_buf_uid = auto_name('vertbuf')
        self._draw_cmd_uid = auto_name('drawcmd')
        self._material_uid = 'default'

    def _create_draw_array(self):
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
        return num_triangles, verts

    def draw(self, view):
        if not self._view_needs_update:
            return

        bytes_per_float32 = 4
        num_triangles, vert_nors = self.create_draw_array()
        view.update_buffer(self._vert_buf_uid, vert_nors)
        view.update_draw_command({
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
            'uniforms': {
                'model':
                None # TODO MatrixUniform(self._transform.matrix())
            },
            'range': (0, num_triangles),
            'primitive': 'triangles'
        })
