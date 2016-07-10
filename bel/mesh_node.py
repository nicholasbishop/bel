import numpy

from bel.auto_name import auto_name
from bel.buffer_object import float_array_buffer_view
from bel.draw_command import DrawCommand
from bel.mesh import Mesh
from bel.scene_node import SceneNode
from bel.uniform import MatrixUniform
from cgmath.normal import triangle_normal
from cgmath.vector import copy_xyz

class MeshNode(SceneNode):
    def __init__(self, mesh=None):
        super().__init__()
        self._mesh = Mesh() if mesh is None else mesh
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
            for vi0, vi1, vi2 in face.iter_triangle_fan():
                locs = [
                    self._mesh.verts[vit].loc
                    for vit in (vi0, vi1, vi2)
                ]
                nor = triangle_normal(*locs)

                for loc in locs:
                    copy_xyz(verts[out:out+3], loc)
                    out += 3
                    copy_xyz(verts[out:out+3], nor)
                    out += 3
        return num_triangles, verts

    def _update_vert_buf(self, draw_state):
        num_triangles, vert_nors = self._create_draw_array()
        draw_state.update_buffer(self._vert_buf_uid, vert_nors)
        self._num_draw_triangles = num_triangles

    def _update_draw_cmd(self, draw_state):
        # TODO, update instead of create
        bytes_per_float32 = 4
        dcom = draw_state.get_or_create_draw_command(self._draw_cmd_uid)
        dcom.attributes.update({
            'vert_loc': {
                'buffer': self._vert_buf_uid,
                'buffer_view': float_array_buffer_view(
                    components=3,
                    stride_in_bytes=bytes_per_float32 * 6,
                    offset_in_bytes=0),
            },
            'vert_nor': {
                'buffer': self._vert_buf_uid,
                'buffer_view': float_array_buffer_view(
                    components=3,
                    stride_in_bytes=bytes_per_float32 * 6,
                    offset_in_bytes=bytes_per_float32 * 3)
            }
        })
        dcom.uniforms['model'] = MatrixUniform(self.transform.matrix())
        dcom.vert_range = (0, self._num_draw_triangles * 3)
        dcom.primitive = DrawCommand.Triangles

    def draw(self, draw_state):
        if self._vert_buf_dirty:
            self._update_vert_buf(draw_state)
            self._vert_buf_dirty = False

        if self._draw_cmd_dirty:
            self._update_draw_cmd(draw_state)
            self._draw_cmd_dirty = False
