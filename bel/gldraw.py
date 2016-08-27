from collections import OrderedDict
from logging import getLogger

import attr
from OpenGL.GL import (GL_COLOR_BUFFER_BIT,
                       GL_DEPTH_BUFFER_BIT,
                       GL_DEPTH_TEST,
                       glClear,
                       glClearColor,
                       glDrawArrays,
                       glEnable,
                       glViewport)

from bel.buffer_object import ArrayBufferObject
from bel.color import Color
from bel.draw_command import DrawCommand
from bel.uniform import MatrixUniform, VectorUniform


LOG = getLogger(__name__)

@attr.s
class DrawState:
    # pylint: disable=unsubscriptable-object,unsupported-membership-test
    fb_size = attr.ib(default=(0, 0))
    clear_color = attr.ib(default=Color(0.4, 0.4, 0.5, 1.0))
    _buffer_objects = attr.ib(default=OrderedDict())
    _draw_commands = attr.ib(default=OrderedDict())
    _materials = attr.ib(default=OrderedDict())
    _uniforms = attr.ib(default=OrderedDict())

    def update_buffer(self, uid, array):
        buffer_object = self._buffer_objects.get(uid)
        if buffer_object is None:
            buffer_object = ArrayBufferObject()
            self._buffer_objects[uid] = buffer_object
        buffer_object.set_data(array)

    def get_or_create_draw_command(self, handle):
        draw_command = self._draw_commands.get(handle.uid)
        if draw_command is None:
            draw_command = DrawCommand()
            self._draw_commands[handle.uid] = draw_command
        return draw_command

    # TODO(nicholasbishop): actually update instead of add
    def update_shader_program(self, uid, shader_program):
        if uid in self._materials:
            raise NotImplementedError()
        self._materials[uid] = shader_program

    # TODO(nicholasbishop): actually update instead of add
    def update_matrix_uniform(self, uid, matrix):
        self._uniforms[uid] = MatrixUniform(matrix)

    # TODO(nicholasbishop): actually update instead of add
    def update_vector_uniform(self, uid, vec):
        self._uniforms[uid] = VectorUniform(vec)

    def _draw_one(self, item):
        first, count = item.vert_range

        # Skip empty draws
        if count == 0:
            return

        item.vao.bind()

        material_uid = item.material_name
        if material_uid not in self._materials:
            LOG.error('unknown material: %r', material_uid)
            return

        material = self._materials[material_uid]
        with material.bind():
            material.bind_attributes(self._buffer_objects, item.attributes)
            uniforms = dict(item.uniforms)
            # TODO
            uniforms.update(self._uniforms)
            # TODO
            material.bind_uniforms(uniforms)

        with material.bind():
            glDrawArrays(item.primitive, first, count)

    def aspect_ratio(self):
        height = self.fb_size[1]
        if height == 0:
            return 0
        else:
            return self.fb_size[0] / height

    def draw_all(self):
        glViewport(0, 0, *self.fb_size)

        self.update_vector_uniform('fb_size', self.fb_size)

        glClearColor(*self.clear_color.as_tuple())
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        for comm in self._draw_commands.values():
            self._draw_one(comm)
