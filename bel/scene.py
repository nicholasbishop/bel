import numpy
from pyrr import Matrix44, Vector3
from pyrr.vector3 import generate_normals

from bel.uniform import MatrixUniform
from bel.window import WindowClient

class Scene:
    def __init__(self):
        self._window = WindowClient(self)
        self._root = SceneNode()
        self._camera = SceneNode()
        self._root.add(self._camera)

        # TODO
        self._window.conn.send_msg({
            'tag': 'update_material',
            'uid': 'default',
            'vert_shader_paths': ['shaders/vert.glsl'],
            'frag_shader_paths': ['shaders/frag.glsl'],
        })

    def handle_event(self, msg):
        tag = msg['tag']
        if tag == 'event_mouse_button':
            print(msg)

    def ray_cast(self, ray):
        class Hit:
            def __init__(self):
                self.node = None
                self.t = None

        hit = Hit()
        # TODO, implement properly
        iter_nodes(lambda node: node.ray_cast(hit))

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

        self.iter_nodes(SceneNode._bake_transform)
        self.iter_nodes(lambda node: node.draw(self))

    def load_path(self, path):
        node = MeshNode.load_obj(path)
        self.root.add(node)
        node.send(self, self._window.conn)
        return node

    def run(self):
        pass


class SceneNode:
    def __init__(self):
        self._parent = None
        self._children = []
        # TODO
        self._baked_transform = Matrix44.from_translation(Vector3([0, 0, -2]))

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
                    vec = Vector3()
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

    def create_draw_array(self):
        elem_per_vert = 6
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

                locs = [self.verts[vit].loc for vit in (vi0, vi1, vi2)]
                nor = Vector3(generate_normals(*locs))

                for loc in locs:
                    verts[out + 0] = loc.x
                    verts[out + 1] = loc.y
                    verts[out + 2] = loc.z
                    verts[out + 3] = nor.x
                    verts[out + 4] = nor.y
                    verts[out + 5] = nor.z
                    out += 6
        return verts

    def send(self, scene, conn):
        vert_nors = self.create_draw_array()
        num_triangles = len(vert_nors) // 6
        bytes_per_float32 = 4

        conn.send_msg({
            'tag': 'update_buffer',
            'name': 'buffer0',
            'contents': vert_nors
        })

        conn.send_msg({
            'tag': 'draw_arrays',
            'material': 'default',
            'attributes': {
                'vert_loc': {
                    'buffer': 'buffer0',
                    'components': 3,
                    'gltype': 'float',
                    'normalized': False,
                    'offset': 0,
                    'stride': bytes_per_float32 * 6
                },
                'vert_nor': {
                    'buffer': 'buffer0',
                    'components': 3,
                    'gltype': 'float',
                    'normalized': False,
                    'offset': bytes_per_float32 * 3,
                    'stride': bytes_per_float32 * 6
                }
            },
            'uniforms': {
                'model_view':
                MatrixUniform(self._baked_transform)
            },
            'range': (0, num_triangles),
            'primitive': 'triangles'
        })
