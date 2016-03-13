from socket import AF_UNIX, SOCK_STREAM, socket
import logging

import sys
from OpenGL import GL as gl

from bel import ipc
from bel.shader import ShaderProgram
from bel.buffer_object import ArrayBufferObject

def cb_handle_dbg_msg(*args):
    msg = args[5]
    logging.info('glDebugMessage: %s', msg.decode())

class WindowServer:
    def __init__(self, sock, glfw):
        self.conn = ipc.Conn(sock)
        self.glfw = glfw
        self.window = None
        self.resources = {}
        self.buffer_objects = {}
        self.draw_list = []
        self.materials = {}

    def run(self):
        self.window = self.glfw.CreateWindow(640, 480, 'bel.WindowServer')
        self.glfw.MakeContextCurrent(self.window)

        if gl.glDebugMessageCallback:
            callback = gl.GLDEBUGPROC(cb_handle_dbg_msg)
            gl.glDebugMessageCallback(callback, None)

        while not self.glfw.WindowShouldClose(self.window):
            self.draw()

            self.glfw.SwapBuffers(self.window)
            self.glfw.PollEvents()
            msg = self.conn.read_msg_nonblocking()
            if msg is not None:
                self.handle_msg(msg)

    def handle_msg(self, msg):
        tag = msg['tag']
        if tag == 'update_buffer':
            name = msg['name']
            if name not in self.buffer_objects:
                self.buffer_objects[name] = ArrayBufferObject()
            self.buffer_objects[name].set_data(msg['contents'])
        elif tag == 'draw_arrays':
            self.draw_list.append(msg)
        elif tag == 'update_material':
            uid = msg['uid']
            if uid not in self.materials:
                self.materials[uid] = ShaderProgram()
            self.materials[uid].update(msg)

    def draw(self):
        # TODO
        gl.glClearColor(0.3, 0.3, 0.4, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        width, height = self.glfw.GetFramebufferSize(self.window)
        gl.glViewport(0, 0, width, height)

        for item in self.draw_list:
            material = self.materials[item['material']]
            with material.bind():
                material.bind_attributes(self.buffer_objects, item['attributes'])
                material.bind_uniforms(item['uniforms'])

            first, count = item['range']
            # TODO
            assert item['primitive'] == 'triangles'
            mode = gl.GL_TRIANGLES
            #mode = gl.GL_POINTS
            logging.debug('glDrawArrays(%s, first=%d, count=%d',
                          mode.name, first, count)
            # TODO
            #count = 2
            with material.bind():
                gl.glDrawArrays(mode, first, count)

def window_server_main(server_sock):
    logging.basicConfig(level=logging.INFO, format=
                        '%(levelname)s: window process '
                        '[%(filename)s:%(lineno)d] %(message)s')

    # pylint: disable=locally-disabled,no-member
    import cyglfw3 as glfw
    if not glfw.Init():
        raise RuntimeError('glfw.Init failed')

    glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    #glfw.WindowHint(glfw.OPENGL_DEBUG_CONTEXT, True)

    window = WindowServer(server_sock, glfw)
    window.run()


def main():
    socket_path = sys.argv[1]
    sock = socket(AF_UNIX, SOCK_STREAM)
    sock.connect(socket_path)
    window_server_main(sock)


if __name__ == '__main__':
    main()
