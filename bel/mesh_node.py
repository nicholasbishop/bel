import numpy

from bel.auto_name import auto_name
from bel.scene_node import SceneNode
from bel.uniform import MatrixUniform
from cgmath.normal import triangle_normal

class MeshNode(SceneNode):
    def __init__(self, mesh):
        super().__init__()
        self._mesh = mesh
        self._vert_buf_dirty = True
        self._draw_cmd_dirty = True
        self._num_draw_triangles = 0
        self._vert_buf_uid = auto_name('vertbuf')
        self._draw_cmd_uid = auto_name('drawcmd')
        self._material_uid = 'default'

    def _create_draw_array(self):
        elem_per_vert = 6
        vert_per_tri = 3
        fac = elem_per_vert * vert_per_tri

        num_triangles = 0
        for face in self._mesh.faces:
            num_triangles += len(face.vert_indices) - 2

        verts = numpy.empty(num_triangles * fac, numpy.float32)
        out = 0

        for face in self._mesh.faces:
            vi0 = face.vert_indices[-1]
            for i in range(len(face.vert_indices) - 2):
                vi1 = face.vert_indices[i]
                vi2 = face.vert_indices[i + 1]

                locs = [
                    self._mesh.verts[vit].loc
                    for vit in (vi0, vi1, vi2)
                ]
                nor = triangle_normal(*locs)

                for loc in locs:
                    verts[out + 0] = loc.x
                    verts[out + 1] = loc.y
                    verts[out + 2] = loc.z
                    verts[out + 3] = nor.x
                    verts[out + 4] = nor.y
                    verts[out + 5] = nor.z
                    out += 6
        return num_triangles, verts

    def _update_vert_buf(self, draw_state):
        num_triangles, vert_nors = self._create_draw_array()
        draw_state.update_buffer(self._vert_buf_uid, vert_nors)
        self._num_draw_triangles = num_triangles

    def _update_draw_cmd(self, draw_state):
        bytes_per_float32 = 4
        draw_state.update_draw_command(self._draw_cmd_uid, {
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
                'model': MatrixUniform(self.transform.matrix().numpy_matrix)
            },
            'range': (0, self._num_draw_triangles * 3),
            'primitive': 'triangles'
        })

    def draw(self, draw_state):
        if self._vert_buf_dirty:
            self._update_vert_buf(draw_state)
            self._vert_buf_dirty = False

        if self._draw_cmd_dirty:
            self._update_draw_cmd(draw_state)
            self._draw_cmd_dirty = False
