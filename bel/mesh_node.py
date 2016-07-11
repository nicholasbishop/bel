"""MeshNode is a SceneNode containing one Mesh."""

import numpy

from bel.auto_name import auto_name
from bel.buffer_object import float_array_buffer_view
from bel.draw_command import DrawCommand, DrawCommandHandle
from bel.mesh import Mesh
from bel.scene_node import SceneNode
from bel.uniform import MatrixUniform, VectorUniform
from cgmath.normal import triangle_normal
from cgmath.vector import copy_xyz, vec4


class VertBufHandle:
    def __init__(self):
        self.uid = auto_name('vertbuf')
        # TODO: this will probably need more fine-grained control,
        # i.e. dirty ranges
        self.dirty = True


class MeshNode(SceneNode):
    """SceneNode containing one Mesh."""

    def __init__(self, mesh=None):
        super().__init__()
        self._mesh = Mesh() if mesh is None else mesh

        self._num_draw_triangles = 0
        self._triangle_buf = VertBufHandle()
        self._triangle_draw = DrawCommandHandle()

        self._num_draw_edges = 0
        self._edge_buf = VertBufHandle()
        self._edge_draw = DrawCommandHandle()

        self._material_uid = 'default'
        self._draw_edges = False

    @property
    def draw_edges(self):
        return self._draw_edges

    @draw_edges.setter
    def draw_edges(self, val):
        self._draw_edges = val

    @property
    def mesh(self):
        return self._mesh

    def _create_edge_array(self):
        num_edges = len(self._mesh.edges)
        vert_per_edge = 2
        elem_per_vert = 3
        elem_per_edge = vert_per_edge * elem_per_vert
        verts = numpy.empty(num_edges * elem_per_edge, numpy.float32)

        out_index = 0
        for edge in self._mesh.edges:
            for vert_index in edge.vert_indices:
                vert = self._mesh.vert(vert_index)
                copy_xyz(verts[out_index:], vert.loc)
                out_index += elem_per_vert

        return num_edges, verts

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

    def _update_triangle_buf(self, draw_state):
        self._num_draw_triangles, vert_nors = self._create_draw_array()
        draw_state.update_buffer(self._triangle_buf.uid, vert_nors)

    def _update_edge_buf(self, draw_state):
        self._num_draw_edges, array = self._create_edge_array()
        draw_state.update_buffer(self._edge_buf.uid, array)

    def _update_draw_cmd(self, draw_state):
        # TODO, update instead of create
        bytes_per_float32 = 4
        dcom = draw_state.get_or_create_draw_command(self._triangle_draw)
        dcom.attributes.update({
            'vert_loc': {
                'buffer': self._triangle_buf.uid,
                'buffer_view': float_array_buffer_view(
                    components=3,
                    stride_in_bytes=bytes_per_float32 * 6,
                    offset_in_bytes=0),
            },
            'vert_nor': {
                'buffer': self._triangle_buf.uid,
                'buffer_view': float_array_buffer_view(
                    components=3,
                    stride_in_bytes=bytes_per_float32 * 6,
                    offset_in_bytes=bytes_per_float32 * 3)
            }
        })
        dcom.uniforms['model'] = MatrixUniform(self.transform.matrix())
        dcom.vert_range = (0, self._num_draw_triangles * 3)
        dcom.primitive = DrawCommand.Triangles

    def _update_edge_draw(self, draw_state):
        # TODO, update instead of create
        bytes_per_float32 = 4
        dcom = draw_state.get_or_create_draw_command(self._edge_draw)
        dcom.attributes.update({
            'vert_loc': {
                'buffer': self._edge_buf.uid,
                'buffer_view': float_array_buffer_view(
                    components=3),
            }
        })
        dcom.material_name = 'flat'
        dcom.uniforms['flat_color'] = VectorUniform(vec4(1, 0, 0, 1))
        dcom.uniforms['model'] = MatrixUniform(self.transform.matrix())
        dcom.vert_range = (0, self._num_draw_edges * 2)
        dcom.primitive = DrawCommand.Lines

    def draw(self, draw_state):
        if self._edge_buf.dirty and self._draw_edges:
            self._update_edge_buf(draw_state)
            self._edge_buf.dirty = False

        if self._edge_draw.needs_update and self._draw_edges:
            self._update_edge_draw(draw_state)
            self._edge_draw.needs_update = False

        if self._triangle_buf.dirty:
            self._update_triangle_buf(draw_state)
            self._triangle_buf.dirty = False

        if self._triangle_draw.needs_update:
            self._update_draw_cmd(draw_state)
            self._triangle_draw.needs_update = False
