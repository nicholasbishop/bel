from logging import getLogger

from OpenGL.GL import (GL_COLOR_BUFFER_BIT,
                       GL_DEPTH_BUFFER_BIT,
                       GL_DEPTH_TEST,
                       GL_LINES,
                       GL_POINTS,
                       GL_TRIANGLES,
                       glClear,
                       glClearColor,
                       glDrawArrays,
                       glEnable,
                       glViewport)

from bel.buffer_object import ArrayBufferObject
from bel.color import Color
from bel.draw_command import DrawCommand
from bel.uniform import MatrixUniform, VectorUniform


class DrawState:
    def __init__(self):
        self._log = getLogger(__name__)
        self._fb_size = (0, 0)
        self._clear_color = Color(0.4, 0.4, 0.5, 1.0)
        self._buffer_objects = {}
        self._draw_commands = {}
        self._materials = {}
        self._uniforms = {}

    @property
    def fb_size(self):
        return self._fb_size

    @fb_size.setter
    def fb_size(self, pair):
        self._fb_size = pair
        self.update_vector_uniform('fb_size', self._fb_size)

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

        material_uid = item.material_name
        if material_uid not in self._materials:
            self._log.error('unknown material: %r', material_uid)
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
        height = self._fb_size[1]
        if height == 0:
            return 0
        else:
            return self._fb_size[0] / height

    def draw_all(self):
        glViewport(0, 0, *self._fb_size)

        glClearColor(*self._clear_color.as_tuple())
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        for comm in self._draw_commands.values():
            self._draw_one(comm)
