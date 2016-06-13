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
from pyrr.matrix44 import create_perspective_projection_matrix

from bel.buffer_object import ArrayBufferObject
from bel.color import Color
from bel.shader import ShaderProgram
from bel.uniform import MatrixUniform


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

    def _add_default_materials(self):
        # TODO
        default = ShaderProgram()
        default.update({
            'vert_shader_paths': ['shaders/vert.glsl'],
            'frag_shader_paths': ['shaders/frag.glsl'],
        })
        flat = ShaderProgram()
        flat.update({
            'vert_shader_paths': ['shaders/flat.vert.glsl'],
            'frag_shader_paths': ['shaders/flat.frag.glsl'],
        })
        self.update_shader_program('default', default)
        self.update_shader_program('flat', flat)

    def update_buffer(self, uid, array):
        buffer_object = self._buffer_objects.get(uid)
        if buffer_object is None:
            buffer_object = ArrayBufferObject()
            self._buffer_objects[uid] = buffer_object
        buffer_object.set_data(array)

    def update_draw_command(self, uid, draw_command):
        self._draw_commands[uid] = draw_command

    # TODO(nicholasbishop): actually update instead of add
    def update_shader_program(self, uid, shader_program):
        if uid in self._materials:
            raise NotImplementedError()
        self._materials[uid] = shader_program

    def update_matrix_uniform(self, uid, matrix):
        self._uniforms[uid] = MatrixUniform(matrix.numpy_matrix)

    def _draw_one(self, item, builtin_uniforms):
        material_uid = item['material']
        if material_uid not in self._materials:
            self._log.error('unknown material: %r', material_uid)
            return

        material = self._materials[material_uid]
        with material.bind():
            material.bind_attributes(self._buffer_objects, item['attributes'])
            uniforms = dict(item['uniforms'])
            # TODO
            uniforms.update(builtin_uniforms)
            uniforms.update(self._uniforms)
            # TODO
            material.bind_uniforms(uniforms)

        first, count = item['range']
        # TODO
        primitive = item['primitive']
        if primitive == 'triangles':
            mode = GL_TRIANGLES
        elif primitive == 'lines':
            mode = GL_LINES
        elif primitive == 'points':
            mode = GL_POINTS
        else:
            raise NotImplementedError()

        with material.bind():
            glDrawArrays(mode, first, count)

    def _aspect_ratio(self):
        height = self._fb_size[1]
        if height == 0:
            return 0
        else:
            return self._fb_size[0] / height

    def draw_all(self):
        # TODO(nicholasbishop): better place for this call
        if not self._materials:
            self._add_default_materials()

        glViewport(0, 0, *self._fb_size)

        glClearColor(*self._clear_color.as_tuple())
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        # TODO
        fovy = 90
        aspect = self._aspect_ratio()
        near = 0.01
        far = 100
        proj_matrix = create_perspective_projection_matrix(
            fovy,
            aspect,
            near,
            far,
        )

        # TODO
        builtin_uniforms = {
            'projection': MatrixUniform(proj_matrix),
        }

        for comm in self._draw_commands.values():
            self._draw_one(comm, builtin_uniforms)
