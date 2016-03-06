import logging
from multiprocessing import Process
import os
from socket import socketpair

from OpenGL import GL as gl

from bel import ipc
from bel.shader import ShaderProgram
from bel.buffer_object import ArrayBufferObject

class WindowServer:
    def __init__(self, sock, glfw):
        self.conn = ipc.Conn(sock)
        self.command_buffer = None
        self.glfw = glfw
        self.resources = {}
        self.buffer_objects = {}
        self.draw_list = []
        self.materials = {}

    def run(self):
        window = self.glfw.CreateWindow(640, 480, 'bel.WindowServer')
        self.glfw.MakeContextCurrent(window)

        while not self.glfw.WindowShouldClose(window):
            self.draw()

            self.glfw.SwapBuffers(window)
            self.glfw.PollEvents()
            msg = self.conn.read_msg_nonblocking()
            if msg is not None:
                if hasattr(msg, 'draw'):
                    self.command_buffer = msg
                elif hasattr(msg, 'keys') and 'tag' in msg:
                    self.handle_msg(msg)
                else:
                    msg(self.resources)
                    # ret = msg()
                    # self.conn.send_msg(ret)

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
        if self.command_buffer is not None:
            self.command_buffer.draw(self.resources)
        for item in self.draw_list:
            material = self.materials[item['material']]
            with material.bind():
                material.bind_attributes(self.buffer_objects, item['attributes'])
                material.bind_uniforms(item['uniforms'])

            first, count = item['range']
            # TODO
            assert item['primitive'] == 'triangles'
            mode = gl.GL_TRIANGLES
            logging.debug('glDrawArrays(%s, first=%d, count=%d',
                          mode.name, first, count)
            with material.bind():
                gl.glDrawArrays(mode, first, count)


def window_server_main(server_sock):
    #print('verify', os.environ['LD_PRELOAD'])
    logging.basicConfig(level=logging.INFO, format=
                        '%(levelname)s: window process '
                        '[%(filename)s:%(lineno)d] %(message)s')

    # pylint: disable=locally-disabled,no-member
    import cyglfw3 as glfw
    if not glfw.Init():
        raise RuntimeError('glfw.Init failed')

    #version = 3,2
    # glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, version[0])
    # glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, version[1])
    # # glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, 1)
    # # glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # glfw.WindowHint(glfw.OPENGL_DEBUG_CONTEXT, True)
    glfw.WindowHint( glfw.CLIENT_API, glfw.OPENGL_ES_API );
    glfw.WindowHint( glfw.CONTEXT_VERSION_MAJOR, 2 );

    window = WindowServer(server_sock, glfw)
    window.run()


class WindowClient:
    def __init__(self):
        # TODO(nicholasbishop): verify that the defaults for
        # socketpair guarantee message ordering
        sock, server_sock = socketpair()
        self.conn = ipc.Conn(sock)
        # tracelib = '/home/nicholasbishop/apitrace/build/wrappers/glxtrace.so'
        # os.environ['LD_PRELOAD'] = tracelib
        self.proc = Process(target=window_server_main, args=(server_sock,))
        self.proc.start()

    def send_msg(self, msg):
        self.conn.send_msg(msg)

    def read_msg_blocking(self):
        return self.conn.read_msg_blocking()
