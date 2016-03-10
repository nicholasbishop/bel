from socket import AF_UNIX, SOCK_STREAM, socket
import logging
import os
import subprocess

import sys
from OpenGL import GL as gl

from bel import ipc
from bel.shader import ShaderProgram
from bel.buffer_object import ArrayBufferObject

def handle_dbg_msg(source, msg_type, msg_id, msg_severity, msg_length, msg, user_data):
    print('here')

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

        gl.glDebugMessageCallback(gl.GLDEBUGPROC(handle_dbg_msg), None)

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
        # TODO
        gl.glClearColor(0.3, 0.3, 0.4, 0.0)
        #gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glViewport(0, 0, 640, 480)

        for item in self.draw_list:
            material = self.materials[item['material']]
            with material.bind():
                material.bind_attributes(self.buffer_objects, item['attributes'])
                material.bind_uniforms(item['uniforms'])

            first, count = item['range']
            # TODO
            assert item['primitive'] == 'triangles'
            #mode = gl.GL_TRIANGLES
            mode = gl.GL_POINTS
            logging.debug('glDrawArrays(%s, first=%d, count=%d',
                          mode.name, first, count)
            # TODO
            count = 2
            with material.bind():
                gl.glDrawArrays(mode, first, count)

def window_server_main(server_sock):
    #print('verify', os.environ['LD_PRELOAD'])
    logging.basicConfig(level=logging.INFO, format=
                        '%(levelname)s: window process '
                        '[%(filename)s:%(lineno)d] %(message)s')

    # pylint: disable=locally-disabled,no-member
    import time
    print(4)
    import cyglfw3 as glfw
    print(5)
    if not glfw.Init():
        print(7)
        raise RuntimeError('glfw.Init failed')
    print(6)

    glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.WindowHint(glfw.OPENGL_DEBUG_CONTEXT, True)
    #glfw.WindowHint( glfw.CLIENT_API, glfw.OPENGL_ES_API );
    #glfw.WindowHint( glfw.CONTEXT_VERSION_MAJOR, 2 );

    print(7)
    window = WindowServer(server_sock, glfw)
    window.run()


def main():
    socket_path = sys.argv[1]
    print(socket_path)
    print('proc 1')
    sock = socket(AF_UNIX, SOCK_STREAM)
    print('proc 2')
    sock.connect(socket_path)
    print('proc 3')
    
    window_server_main(sock)
    print('proc 4')


if __name__ == '__main__':
    main()
