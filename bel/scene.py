import numpy
from pyrr import Matrix44, Quaternion, Vector3, Vector4, vector
from pyrr.vector3 import generate_normals

from bel.auto_name import auto_name
from bel.event import InputManager
from bel.transform import Transform, deg_to_rad
from bel.uniform import MatrixUniform, VectorUniform
from bel.window import WindowClient

class EventHandler:
    def __init__(self, scene):
        self._scene = scene
        self._input_manager = None

    def set_input_manager(self, input_manager):
        self._input_manager = input_manager

    def mouse_down(self, button):
        #     # TODO
        #     ray = self.create_ray_from_mouse(msg)
        #     #self.add_line(Vector3((0, 0, 0)), ray)
        # node = self._scene.root.children[1]
        # node.transform.rotate(Quaternion.from_z_rotation(deg_to_rad(30)))
        # node.send(self._scene._window.conn)
        pass

    def mouse_up(self, button):
        pass

    def mouse_drag(self, pos):
        node = self._scene.root.children[1]
        node.transform.set_translation([pos[0], pos[1], -2])
        node.send(self._scene._window.conn)

    def mouse_move(self, pos):
        pass


class Scene:
    def __init__(self):
        self._event_handler = EventHandler(self)
        self._input_manager = InputManager(self._event_handler)
        self._window = WindowClient(self)
        self._root = SceneNode()
        self._camera = SceneNode()
        self._root.add(self._camera)

        # TODO
        self._send_default_materials()

    def _send_default_materials(self):
        self._window.conn.send_msg({
            'tag': 'update_material',
            'uid': 'default',
            'vert_shader_paths': ['shaders/vert.glsl'],
            'frag_shader_paths': ['shaders/frag.glsl'],
        })
        self._window.conn.send_msg({
            'tag': 'update_material',
            'uid': 'flat',
            'vert_shader_paths': ['shaders/flat.vert.glsl'],
            'frag_shader_paths': ['shaders/flat.frag.glsl'],
        })

    def handle_event(self, msg):
        self._input_manager.feed(msg)

    def create_ray_from_mouse(self, mouse):
        # TODO
        view_matrix = Matrix44.identity()
        
        # http://antongerdelan.net/opengl/raycasting.html
        ray_clip = Vector4((mouse['x'], mouse['y'], -1.0, 1.0))
        ray_eye = mouse['projection_matrix'].inverse * ray_clip
        ray_eye.w = -1.0
        ray_eye.z = 0.0
        ray_world, _ = (view_matrix.inverse * ray_eye).vector3;
        ray_world.normalise()
        return ray_world

    def add_line(self, start_point, end_point):
        node = LineNode(start_point, end_point)
        self.root.add(node)
        # TODO...
        node.send(self._window.conn)
        return node

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

    def load_path(self, path):
        node = MeshNode.load_obj(path)
        self.root.add(node)
        node.send(self._window.conn)
        return node

    def run(self):
        pass


class SceneNode:
    def __init__(self):
        self._parent = None
        self._children = []
        self._transform = Transform()
        # TODO
        self._transform.translate(Vector3((0, 0, -2)))

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


def obj_remove_comment(line):
    ind = line.find('#')
    if ind != -1:
        line = line[:ind].rstrip()
    return line


class LineNode(SceneNode):
    def __init__(self, start_point, end_point):
        super().__init__()
        self.start_point = start_point
        self.end_point = end_point
        self._vert_buffer = auto_name('buffer')

    def send(self, conn):
        verts = numpy.empty(6, numpy.float32)
        verts[0] = self.start_point.x
        verts[1] = self.start_point.y
        verts[2] = self.start_point.z
        verts[3] = self.end_point.x
        verts[4] = self.end_point.y
        verts[5] = self.end_point.z

        conn.send_msg({
            'tag': 'update_buffer',
            'name': self._vert_buffer,
            'contents': verts
        })

        conn.send_msg({
            'tag': 'draw_arrays',
            'material': 'flat',
            'attributes': {
                'vert_loc': {
                    'buffer': self._vert_buffer,
                    'components': 3,
                    'gltype': 'float',
                    'normalized': False,
                    'offset': 0,
                    'stride': 0
                },
            },
            'uniforms': {
                'model_view':
                MatrixUniform(self._transform.matrix()),
                'flat_color': VectorUniform(Vector4((1, 0, 0, 1)))
            },
            'range': (0, 2),
            'primitive': 'lines'
        })
        

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
        self._vert_buffer = auto_name('buffer')
        self._draw_arrays_name = auto_name('draw_arrays')

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

    def send(self, conn):
        vert_nors = self.create_draw_array()
        num_triangles = len(vert_nors) // 6
        bytes_per_float32 = 4

        conn.send_msg({
            'tag': 'update_buffer',
            'name': self._vert_buffer,
            'contents': vert_nors
        })

        conn.send_msg({
            'tag': 'draw_arrays',
            'name': self._draw_arrays_name,
            'material': 'default',
            'attributes': {
                'vert_loc': {
                    'buffer': self._vert_buffer,
                    'components': 3,
                    'gltype': 'float',
                    'normalized': False,
                    'offset': 0,
                    'stride': bytes_per_float32 * 6
                },
                'vert_nor': {
                    'buffer': self._vert_buffer,
                    'components': 3,
                    'gltype': 'float',
                    'normalized': False,
                    'offset': bytes_per_float32 * 3,
                    'stride': bytes_per_float32 * 6
                }
            },
            'uniforms': {
                'model_view':
                MatrixUniform(self._transform.matrix())
            },
            'range': (0, num_triangles),
            'primitive': 'triangles'
        })
