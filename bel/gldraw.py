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
from pyrr import Matrix44
from pyrr.matrix44 import create_perspective_projection_matrix

from bel.color import Color
from bel.uniform import MatrixUniform


class DrawState:
    def __init__(self):
        self._log = getLogger(__name__)
        self.width = 0
        self.height = 0
        self.clear_color = Color(0.4, 0.4, 0.5, 1.0)
        self.buffer_objects = {}
        self.draw_commands = {}
        self.materials = {}
        self._uniforms = {}

    # TODO(nicholasbishop): actually update instead of add
    def update_shader_program(self, uid, shader_program):
        if uid in self.materials:
            raise NotImplementedError()
        self.materials[uid] = shader_program

    def update_uniform(self, uid, uniform):
        self._uniforms[uid] = uniform

    def _draw_one(self, item, builtin_uniforms):
        material_uid = item['material']
        if material_uid not in self.materials:
            self._log.error('unknown material: %r', material_uid)
            return

        material = self.materials[material_uid]
        with material.bind():
            material.bind_attributes(self.buffer_objects, item['attributes'])
            uniforms = dict(item['uniforms'])
            # TODO
            uniforms.update(builtin_uniforms)
            uniforms.update(self._uniforms)
            # TODO
            uniforms['model'] = MatrixUniform(Matrix44.identity())
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

    def draw_all(self):
        glViewport(0, 0, self.width, self.height)

        glClearColor(*self.clear_color.as_tuple())
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        # TODO
        fovy = 90
        aspect = self.width / self.height
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

        for comm in self.draw_commands.values():
            self._draw_one(comm, builtin_uniforms)
