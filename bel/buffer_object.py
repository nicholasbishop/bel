from collections import namedtuple
from contextlib import contextmanager
from ctypes import c_void_p
import logging

from OpenGL.GL import (GL_ARRAY_BUFFER, GL_FLOAT, GL_STATIC_DRAW,
                       glBindBuffer, glBufferData, glDeleteBuffers,
                       glGenBuffers, glVertexAttribPointer)
import OpenGL.GL as gl

class BufferObject:
    def __init__(self, kind):
        self._kind = kind
        self._hnd = glGenBuffers(1)

        # TODO
        self._vao = gl.glGenVertexArrays(1)

        logging.info('glGenBuffers(1) -> %d', self._hnd)
        if self._hnd == 0:
            raise ValueError('glGenBuffers failed')

    def release(self, conn):
        if self._hnd is not None:
            conn.send_msg(lambda: glDeleteBuffers(self._hnd))

    @contextmanager
    def bind(self):
        glBindBuffer(self._kind, self._hnd)
        try:
            yield
        finally:
            pass
            #glBindBuffer(self._kind, 0)

    def set_data(self, data, usage=None):
        if usage is None:
            usage = GL_STATIC_DRAW

        with self.bind():
            glBufferData(self._kind, data, usage)

    def bind_to_attribute(self, attr_index, buffer_view):
        with self.bind():
            # TODO
            gl.glBindVertexArray(self._vao)

            glVertexAttribPointer(attr_index,
                                  buffer_view.components,
                                  buffer_view.gltype,
                                  buffer_view.normalized,
                                  buffer_view.stride_in_bytes,
                                  c_void_p(buffer_view.offset_in_bytes))


class ArrayBufferObject(BufferObject):
    def __init__(self):
        super().__init__(GL_ARRAY_BUFFER)


ArrayBufferView = namedtuple('ArrayBufferView',
                             ('components',
                              'gltype',
                              'normalized',
                              'stride_in_bytes',
                              'offset_in_bytes'))

def float_array_buffer_view(components,
                            stride_in_bytes,
                            offset_in_bytes):
    return ArrayBufferView(
        components=components,
        gltype=GL_FLOAT,
        normalized=False,
        stride_in_bytes=stride_in_bytes,
        offset_in_bytes=offset_in_bytes)
