from OpenGL import GL as gl
from OpenGL.GL import glUseProgram
import numpy

from bel.math3d import (Mat4x4, Transform, Vec2, Vec3,
                        perspective_matrix)
from bel.window import WindowClient
from bel import shader
from bel.shader import ShaderProgram
from bel.buffer_object import ArrayBufferObject
from bel.uniform import MatrixUniform

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
        self._projection_matrix = numpy.identity(4)
        self._root = SceneNode()
        self._camera = SceneNode()
        self._root.add(self._camera)

        # TODO
        viewport_size = Vec2(640, 480)
        near = 0.01
        far = 100.0
        self._projection_matrix = perspective_matrix(90,
                                                     viewport_size,
                                                     near, far)

        # TODO
        self._window.conn.send_msg({
            'tag': 'update_material',
            'uid': 'default',
            'vert_shader_paths': ['shaders/vert.glsl'],
            'frag_shader_paths': ['shaders/frag.glsl'],
        })

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
        node.send(self, self._window.conn)
        self._send_draw_func()
        return node

    def run(self):
        pass


class SceneNode:
    def __init__(self):
        self._parent = None
        self._children = []
        self._transform = Transform()
        self._baked_transform = numpy.identity(4)

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

    def send(self, scene, conn):
        elem_per_vert = 4
        vert_per_tri = 3
        fac = elem_per_vert * vert_per_tri

        num_triangles = 0
        for face in self.faces:
            num_triangles += len(face.indices) - 2

        verts = numpy.empty(num_triangles * fac, numpy.float32)
        out = 0

        for face in self.faces:
            vi0 = face.indices[-1]
            for i in range(len(face.indices) - 2):
                vi1 = face.indices[i]
                vi2 = face.indices[i + 1]

                for index, vit in enumerate((vi0, vi1, vi2)):
                    vec = self.verts[vit].loc
                    verts[out + 0] = vec.x
                    verts[out + 1] = vec.y
                    verts[out + 2] = vec.z
                    verts[out + 3] = index
                    out += 4

        conn.send_msg({
            'tag': 'update_buffer',
            'name': 'buffer0',
            'contents': verts
        })

        conn.send_msg({
            'tag': 'draw_arrays',
            'material': 'default',
            'attributes': {
                'vert_loc': {
                    'buffer': 'buffer0',
                    'components': 4,
                    'gltype': 'float',
                    'normalized': False,
                    'offset': 0,
                    'stride': 0
                }
            },
            'uniforms': {
                'model_view':
                MatrixUniform(self._baked_transform),
                'projection':
                MatrixUniform(scene.projection_matrix)
            },
            'range': (0, num_triangles),
            'primitive': 'triangles'
        })

    def free_graphics_resources(self, conn):
        self._vert_buffer.release(conn)
        self._shader_program.release(conn)

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
