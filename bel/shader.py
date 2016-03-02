import logging

from OpenGL.GL import (GL_COMPILE_STATUS, GL_FRAGMENT_SHADER,
                       GL_VERTEX_SHADER, glAttachShader,
                       glCompileShader, glCreateProgram,
                       glCreateShader, glDeleteProgram,
                       glDeleteShader, glGetAttribLocation,
                       glGetShaderInfoLog, glGetShaderiv,
                       glLinkProgram, glShaderSource)

KEYWORD_ATTRIBUTE = 'attribute'
KEYWORD_UNIFORM = 'uniform'

def extract_links(source):
    for line in source.splitlines():
        parts = line.split()
        if len(parts) == 3:
            keyword = parts[0]
            name = parts[2].rstrip(';')

            if keyword in (KEYWORD_ATTRIBUTE, KEYWORD_UNIFORM):
                yield keyword, name


class Shader:
    def __init__(self, path, kind):
        self._kind = kind
        self._path = path
        with open(self._path) as rfile:
            self._source = rfile.read()

    def extract_links(self):
        links = list(extract_links(self.source))
        self._attributes = set(lnk[1] for lnk in links if lnk[0] == KEYWORD_ATTRIBUTE)
        self._uniforms = set(lnk[1] for lnk in links if lnk[0] == KEYWORD_UNIFORM)

    @property
    def handle(self):
        return self._hnd

    def alloc(self, conn):
        if self._hnd is not None:
            raise ValueError('shader already has handle')

        def async():
            hnd = glCreateShader(self._kind)
            logging.info('created shader %d', hnd)
            return hnd

        conn.send_msg(async)
        self._hnd = conn.read_msg_blocking()
        if self._hnd == 0:
            raise ValueError('glCreateShader failed')

    def release(self, conn):
        if self._hnd is not None:
            conn.send_msg(lambda: glDeleteShader(self._hnd))

    def compile(self, conn):
        if self._hnd is None:
            raise ValueError('shader not allocated')

        def async():
            with open(self._path) as rfile:
                source = rfile.read()
            glShaderSource(self._hnd, source)
            glCompileShader(self._hnd)

            if glGetShaderiv(self._hnd, GL_COMPILE_STATUS) is False:
                log = glGetShaderInfoLog(self._hnd)
                glDeleteShader(self._hnd)
                raise RuntimeError('shader failed to compile', log)
            logging.info('compiled shader %d', self._hnd)

        conn.send_msg(async)

    def uniforms(self):
        return self._uniforms

    def attributes(self):
        return self._attributes


class VertexShader(Shader):
    def __init__(self, path):
        super().__init__(path, GL_VERTEX_SHADER)


class FragmentShader(Shader):
    def __init__(self, path):
        super().__init__(path, GL_FRAGMENT_SHADER)


class ShaderProgram:
    def __init__(self, uid):
        self._shaders = []
        self._uid = uid

    @property
    def uid(self):
        return self._uid

    def add_vert_shader_from_path(self, path):
        self._shaders.append(VertexShader(path))

    def add_frag_shader_from_path(self, path):
        self._shaders.append(FragmentShader(path))

        # TODO!
        # self._uniforms = {}
        # self._attributes = {}
        # for name in self._vert_shader.uniforms() | self._frag_shader.uniforms():
        #     self._uniforms[name] = glGetUniformLocation(self._hnd, name)
        # for name in self._vert_shader.attributes() | self._frag_shader.attributes():
        #     self._attributes[name] = glGetAttribLocation(self._hnd, name)

    def alloc(self, conn):
        if self._hnd is not None:
            raise ValueError('shader program already has handle')

        def async():
            hnd = glCreateProgram()
            logging.info('created program %d', hnd)
            return hnd

        conn.send_msg(async)
        self._hnd = conn.read_msg_blocking()
        if self._hnd == 0:
            raise ValueError('glCreateProgram failed')

        self._vert_shader.alloc(conn)
        self._frag_shader.alloc(conn)

    def release(self, conn):
        self._vert_shader.release(conn)
        self._frag_shader.release(conn)
        if self._hnd is not None:
            conn.send_msg(lambda: glDeleteProgram(self._hnd))

    def compile_and_link(self, conn):
        self._vert_shader.compile(conn)
        self._frag_shader.compile(conn)

        def async():
            glAttachShader(self._hnd, self._vert_shader.handle)
            glAttachShader(self._hnd, self._frag_shader.handle)
            glLinkProgram(self._hnd)
            logging.info('linked shader program %d', self._hnd)

        conn.send_msg(async)

    @property
    def handle(self):
        return self._hnd

    # TODO!
    # def bind(self):
    #     glUseProgram(self._hnd)

    # def set_uniform(self, key, val):
    #     loc = self._uniforms[key]
    #     if isinstance(val, Mat4x4):
    #         glUniformMatrix4fv(loc, 1, False, val._dat.flatten(order='F'))

    # def get_attribute_location(self, key):
    #     return self._attributes[key]
