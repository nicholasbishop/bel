from contextlib import contextmanager
import logging

from OpenGL.GL import (GL_ARRAY_BUFFER, GL_STREAM_DRAW, glBindBuffer,
                       glBufferData, glDeleteBuffers, glGenBuffers,
                       glVertexAttribPointer)
from OpenGL.GL import glGetInteger, GL_ARRAY_BUFFER_BINDING
import OpenGL.GL as gl
class BufferObject:
    def __init__(self, kind):
        self._kind = kind
        self._hnd = glGenBuffers(1)
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
        print(data)
        if usage is None:
            usage = GL_STREAM_DRAW

        with self.bind():
            glBufferData(self._kind, data, usage)
            logging.info('glBufferData(buffer=%s, %s, ..., %s)', self._hnd,
                         self._kind.name, usage.name)

    def bind_to_attribute(self, attr_index, components, gltype,
                          normalized, stride, offset):
        with self.bind():
            logging.debug('glVertexAttribPointer(index=%d, size=%d, type=%s, '
                          'normalized=%r, stride=%d, pointer=%d',
                          attr_index, components, gltype.name,
                          normalized, stride, offset)

            vao = gl.glGenVertexArrays(1)
            gl.glBindVertexArray(vao)

            glVertexAttribPointer(attr_index,
                                  components,
                                  gltype,
                                  normalized,
                                  stride,
                                  offset)


class ArrayBufferObject(BufferObject):
    def __init__(self):
        super().__init__(GL_ARRAY_BUFFER)
