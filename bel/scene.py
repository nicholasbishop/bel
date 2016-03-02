from OpenGL import GL as gl
from OpenGL.GL import glUseProgram
import numpy

from bel.math3d import (Mat4x4, Transform, Vec3)
from bel.window import WindowClient
from bel import shader
from bel.shader import ShaderProgram
from bel.buffer_object import ArrayBufferObject


class CommandBuffer:
    def __init__(self):
        self.geoms = []

    def draw(self, materials):
        gl.glClearColor(0.3, 0.3, 0.4, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        for geom in self.geoms:
            geom(materials)


class Scene:
    def __init__(self):
        self._command_buffer = CommandBuffer()
        self._window = WindowClient()
        self._projection_matrix = Mat4x4.identity()
        self._root = SceneNode()
        self._camera = SceneNode()
        self._root.add(self._camera)
        self._shader_programs = {}

        # TODO
        default_material = ShaderProgram('default')
        default_material.add_vert_shader_from_path('shaders/vert.glsl')
        default_material.add_frag_shader_from_path('shaders/frag.glsl')
        self.add_shader_program(default_material)

    def add_shader_program(self, shader_program):
        if shader_program.uid in self._shader_programs:
            raise KeyError('shader program with uid already exists', uid)
        self._shader_programs[shader_program.uid] = shader_program

    def _send_draw_func(self):
        self._window.send_msg(self._command_buffer)

    @property
    def projection_matrix(self):
        return self._projection_matrix

    @property
    def root(self):
        return self._root

    def iter_nodes(self, func):
        stack = [self._root]
        while len(stack) != 0:
            node = stack.pop()
            stack += node.children
            func(node)

    def draw(self, viewport_size):
        near = 0.01
        far = 100.0
        self._projection_matrix = Mat4x4.perspective(90,
                                                     viewport_size,
                                                     near, far)

        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.iter_nodes(SceneNode._bake_transform)
        self.iter_nodes(lambda node: node.draw(self))

    def load_path(self, path):
        node = MeshNode.load_obj(path)
        self.root.add(node)
        # node.alloc_graphics_resources(self._window.conn)
        # node.update_graphics_resources(self._window.conn)
        self._command_buffer.geoms.append(node.create_draw_func())
        self._send_draw_func()
        return node

    def run(self):
        pass


class SceneNode:
    def __init__(self):
        self._parent = None
        self._children = []
        self._transform = Transform()
        self._baked_transform = Mat4x4()

    def _bake_transform(self):
        mat = self._transform.matrix()
        if self._parent is None:
            self._baked_transform = mat
        else:
            self._baked_transform = self._parent._baked_transform * mat

    @property
    def transform(self):
        return self._transform

    @property
    def children(self):
        return self._children

    def add(self, child):
        child._parent = self
        self._children.append(child)

    def remove(self, child):
        child._parent = None
        self._children.append(child)

    def draw(self, scene):
    #     subdraw = DrawData()
    #     subdraw.projection = draw_data.projection
    #     subdraw.model_view = subdraw.model_view * self._transform.matrix()

    #     for child in self._children:
    #         child.draw(subdraw)

    #     self.draw_self(subdraw)

    # def draw_self(self, draw_data):
        pass


def obj_remove_comment(line):
    ind = line.find('#')
    if ind != -1:
        line = line[:ind].rstrip()
    return line


class MeshNode(SceneNode):
    class Vert:
        def __init__(self, loc):
            self.loc = loc

    class Face:
        def __init__(self, indices):
            self.indices = indices

    def __init__(self):
        super().__init__()
        self.verts = []
        self.faces = []
        self._vert_buffer = ArrayBufferObject()
        self._material_uid = 'default'

    @staticmethod
    def load_obj(path):
        with open(path) as rfile:
            verts = []
            faces = []
            for line in rfile.readlines():
                line = obj_remove_comment(line)
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
                    verts.append(MeshNode.Vert(vec))
                elif tok == 'f':
                    indices = [int(ind) - 1 for ind in parts[1:]]
                    faces.append(MeshNode.Face(indices))

            mesh = MeshNode()
            mesh.verts = verts
            mesh.faces = faces
            return mesh

    def alloc_graphics_resources(self, conn):
        self._vert_buffer.alloc(conn)
        self._shader_program.alloc(conn)

    def update_graphics_resources(self, conn):
        verts = numpy.empty(1)

        for face in self.faces:
            vi0 = face.indices[-1]
            for i in range(len(face.indices) - 2):
                vi1 = face.indices[i]
                vi2 = face.indices[i + 1]

                for index, vit in enumerate((vi0, vi1, vi2)):
                    vec = self.verts[vit].loc
                    verts += vec.x
                    verts += vec.y
                    verts += vec.z
                    # TODO
                    verts += index

        self._vert_buffer.set_data(conn, verts)

        self._shader_program.compile_and_link(conn)

    def free_graphics_resources(self, conn):
        self._vert_buffer.release(conn)
        self._shader_program.release(conn)

    def create_draw_func(self):
        #shader_program = self._shader_program.handle
        material_uid = self._material_uid
        def draw(materials):
            materials[material_uid].bind()
            pass #glUseProgram(shader_program)
            
        return draw

    def draw(self, scene):
        material = scene.materials[self._material_name]
        def async():
            material
            glUseProgram(self._shader_program.handle)
            self._program.set_uniform('model_view', self._baked_transform)
            self._program.set_uniform('projection', scene.projection_matrix)

        verts = []

        attrib = self._program.get_attribute_location('vert_loc')
        attrib_size = 4  # xyzw

        gl.glEnableVertexAttribArray(attrib)

        normalized = False
        stride = 0

        gl.glVertexAttribPointer(attrib,
                                 attrib_size,
                                 gl.GL_FLOAT,
                                 normalized,
                                 stride,
                                 verts)

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(verts) // 3)

        gl.glDisableVertexAttribArray(attrib)
