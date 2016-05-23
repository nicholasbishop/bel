import logging

from OpenGL import GL as gl
from pyrr import Matrix44
from pyrr.matrix44 import create_perspective_projection_matrix

from bel.child import main
from bel.msg import Msg, Tag
from bel.shader import ShaderProgram
from bel.buffer_object import ArrayBufferObject
from bel.uniform import MatrixUniform

def cb_handle_dbg_msg(*args):
    msg = args[5]
    logging.info('glDebugMessage: %s', msg.decode())


def normalize_mouse(pos, width, height):
    return ((2.0 * pos[0]) / width - 1.0,
            1.0 - (2.0 * pos[1]) / height)


class WindowServer:
    def __init__(self, conn, glfw):
        self.conn = conn
        self.glfw = glfw
        self.window = None
        self.resources = {}
        self.buffer_objects = {}
        self.draw_arrays = {}
        self.materials = {}
        self._clear_color = (0.3, 0.3, 0.4, 0.0)

        # TODO, might not belong here
        self._send_default_materials()

    def _send_default_materials(self):
        self.conn.send_msg(Msg(Tag.WND_UpdateMaterial, {
            'uid': 'default',
            'vert_shader_paths': ['shaders/vert.glsl'],
            'frag_shader_paths': ['shaders/frag.glsl'],
        }))
        self.conn.send_msg(Msg(Tag.WND_UpdateMaterial, {
            'uid': 'flat',
            'vert_shader_paths': ['shaders/flat.vert.glsl'],
            'frag_shader_paths': ['shaders/flat.frag.glsl'],
        }))

    def cb_cursor_pos(self, window, xpos, ypos):
        width, height = self.glfw.GetWindowSize(self.window)
        self.conn.send_msg(Msg(Tag.SCE_EventCursorPosition, {
            'tag': 'event_mouse_move',
            'pos': normalize_mouse((xpos, ypos), width, height)
        }))

    def cb_mouse_button(self, window, button, action, mods):
        width, height = self.glfw.GetWindowSize(self.window)
        x, y = self.glfw.GetCursorPos(self.window)
        action_str = 'press' if action == self.glfw.PRESS else 'release'

        self.conn.send_msg(Msg(Tag.SCE_EventMouseButton, {
            'button': button,
            'action': action_str,
            'mods': mods,
            'pos': normalize_mouse((x, y), width, height)
            # TODO, should go in its own event
            # 'projection_matrix': self._perspective_matrix
        }))

    def cb_window_size(self, window, width, height):
        self.conn.send_msg(Msg(Tag.SCE_EventWindowSize, (width, height)))

    def run(self):
        self.window = self.glfw.CreateWindow(640, 480, 'bel.WindowServer')
        self.glfw.SwapInterval(1)
        self.glfw.MakeContextCurrent(self.window)

        self.glfw.SetCursorPosCallback(self.window, self.cb_cursor_pos)
        self.glfw.SetMouseButtonCallback(self.window, self.cb_mouse_button)
        self.glfw.SetWindowSizeCallback(self.window, self.cb_window_size)

        while not self.glfw.WindowShouldClose(self.window):
            self.draw()

            self.glfw.PollEvents()

            messages = self.conn.read_messages_nonblocking()
            for msg in messages:
                self.handle_msg(msg)

        self.conn.send_msg(Msg(Tag.Exit))

    def handle_msg(self, msg):
        if msg.tag == Tag.WND_SetClearColor:
            # todo: validate color
            self._clear_color = msg.body
        elif msg.tag == Tag.WND_UpdateBuffer:
            uid = msg.body['uid']
            if uid not in self.buffer_objects:
                self.buffer_objects[uid] = ArrayBufferObject()
            self.buffer_objects[uid].set_data(msg.body['array'])
        elif msg.tag == Tag.WND_UpdateDrawCommand:
            self.draw_arrays[msg.body['uid']] = msg.body
        elif msg.tag == Tag.WND_UpdateMaterial:
            uid = msg.body['uid']
            if uid not in self.materials:
                self.materials[uid] = ShaderProgram()
            self.materials[uid].update(msg.body)
        else:
            logging.error('unhandled message tag: %r', msg.tag)

    def _draw_one(self, item, builtin_uniforms):
        material_uid = item['material']
        if material_uid not in self.materials:
            logging.error('unknown material: %r', material_uid)
            return

        material = self.materials[material_uid]
        with material.bind():
            material.bind_attributes(self.buffer_objects, item['attributes'])
            uniforms = dict(item['uniforms'])
            uniforms.update(builtin_uniforms)
            material.bind_uniforms(uniforms)

        first, count = item['range']
        # TODO
        primitive = item['primitive']
        if primitive == 'triangles':
            mode = gl.GL_TRIANGLES
        elif primitive == 'lines':
            mode = gl.GL_LINES
        elif primitive == 'points':
            mode = gl.GL_POINTS
        else:
            raise NotImplementedError()

        with material.bind():
            gl.glDrawArrays(mode, first, count)

    def draw(self):
        # TODO
        gl.glClearColor(*self._clear_color)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        width, height = self.glfw.GetFramebufferSize(self.window)
        gl.glViewport(0, 0, width, height)

        # TODO
        fovy = 90
        aspect = width / height
        near = 0.01
        far = 100
        proj_matrix = create_perspective_projection_matrix(
            fovy,
            aspect,
            near,
            far,
        )

        builtin_uniforms = {
            'projection': MatrixUniform(proj_matrix)
        }

        for item in self.draw_arrays.values():
            self._draw_one(item, builtin_uniforms)
        self.glfw.SwapBuffers(self.window)


def window_server_main(conn):
    # pylint: disable=locally-disabled,no-member
    import cyglfw3 as glfw
    if not glfw.Init():
        raise RuntimeError('glfw.Init failed')

    glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    #glfw.WindowHint(glfw.OPENGL_DEBUG_CONTEXT, True)

    window = WindowServer(conn, glfw)
    window.run()


if __name__ == '__main__':
    main('wnd', window_server_main)
