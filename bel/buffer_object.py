import logging

from OpenGL.GL import (GL_ARRAY_BUFFER, GL_STREAM_DRAW, glBindBuffer,
                       glBufferData, glDeleteBuffers, glGenBuffers)

class BufferObject:
    def __init__(self, kind):
        self._kind = kind
        self._hnd = None

    def alloc(self, conn):
        if self._hnd is not None:
            raise ValueError('buffer already has handle')

        def async():
            hnd = glGenBuffers(1)
            logging.info('created buffer %d', hnd)
            return hnd

        conn.send_msg(async)
        self._hnd = conn.read_msg_blocking()
        if self._hnd == 0:
            raise ValueError('glGenBuffers failed')

    def release(self, conn):
        if self._hnd is not None:
            conn.send_msg(lambda: glDeleteBuffer(self._hnd))

    def set_data(self, conn, data, usage=None):
        if self._hnd is None:
            raise ValueError('shader not allocated')

        if usage is None:
            usage = GL_STREAM_DRAW

        def async():
            glBindBuffer(self._kind, self._hnd)
            glBufferData(self._kind, data, usage)
            logging.info('updated data in buffer %d', self._hnd)
            glBindBuffer(self._kind, 0)

        conn.send_msg(async)


class ArrayBufferObject(BufferObject):
    def __init__(self):
        super().__init__(GL_ARRAY_BUFFER)
