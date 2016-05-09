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
        self._perspective_matrix = None
        self._clear_color = (0.3, 0.3, 0.4, 0.0)

    def cb_cursor_pos(self, window, xpos, ypos):
        # TODO
        width, height = self.glfw.GetWindowSize(self.window)

        self.conn.send_msg({
            'tag': 'event_mouse_move',
            'pos': normalize_mouse((xpos, ypos), width, height)
        })

    def cb_mouse_button(self, window, button, action, mods):
        width, height = self.glfw.GetWindowSize(self.window)
        x, y = self.glfw.GetCursorPos(self.window)

        action_str = 'press' if action == self.glfw.PRESS else 'release'

        norm_x = (2.0 * x) / width - 1.0
        norm_y = 1.0 - (2.0 * y) / height

        self.conn.send_msg({
            'tag': 'event_mouse_button',
            'button': button,
            'action': action_str,
            'mods': mods,
            'x': norm_x,
            'y': norm_y,
            # TODO, should go in its own event
            'projection_matrix': self._perspective_matrix
        })

    def run(self):
        self.window = self.glfw.CreateWindow(640, 480, 'bel.WindowServer')
        self.glfw.SwapInterval(1)
        self.glfw.MakeContextCurrent(self.window)

        self.glfw.SetMouseButtonCallback(self.window, self.cb_mouse_button)
        self.glfw.SetCursorPosCallback(self.window, self.cb_cursor_pos)

        while not self.glfw.WindowShouldClose(self.window):
            self.draw()

            self.glfw.PollEvents()

            msg = self.conn.read_msg_nonblocking()
            if msg is not None:
                self.handle_msg(msg)

        self.conn.send_msg(Msg(Tag.Exit))

    def handle_msg(self, msg):
        if msg.tag == Tag.WND_SetClearColor:
            # todo: validate color
            self._clear_color = msg.body

        # TODO
        return

        tag = msg['tag']
        if tag == 'update_buffer':
            name = msg['name']
            if name not in self.buffer_objects:
                self.buffer_objects[name] = ArrayBufferObject()
            self.buffer_objects[name].set_data(msg['contents'])
        elif tag == 'draw_arrays':
            self.draw_arrays[msg['name']] = msg
        elif tag == 'update_material':
            uid = msg['uid']
            if uid not in self.materials:
                self.materials[uid] = ShaderProgram()
            self.materials[uid].update(msg)
        elif tag == 'exit':
            self.glfw.SetWindowShouldClose(self.window, True)

    def draw(self):
        # TODO
        gl.glClearColor(*self._clear_color)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        width, height = self.glfw.GetFramebufferSize(self.window)
        gl.glViewport(0, 0, width, height)

        builtin_uniforms = {
            'projection': MatrixUniform(self._perspective_matrix)
        }

        for item in self.draw_arrays.values():
            material = self.materials[item['material']]
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

            #mode = gl.GL_POINTS
            logging.debug('glDrawArrays(%s, first=%d, count=%d',
                          mode.name, first, count)
            # TODO
            #count = 2
            with material.bind():
                gl.glDrawArrays(mode, first, count)
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
