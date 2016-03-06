from contextlib import contextmanager
import logging

from OpenGL.GL import (GL_COMPILE_STATUS, GL_FLOAT,
                       GL_FRAGMENT_SHADER, GL_VERTEX_SHADER,
                       glAttachShader, glCompileShader,
                       glCreateProgram, glCreateShader,
                       glDeleteProgram, glDeleteShader,
                       glGetAttribLocation, glGetUniformLocation,
                       glGetShaderInfoLog, glGetShaderiv,
                       glLinkProgram, glShaderSource,
                       glUseProgram)

from bel.uniform import MatrixUniform

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
        self._hnd = None
        self._attributes = set()
        self._uniforms = set()

        self._kind = kind
        self._path = path
        with open(self._path) as rfile:
            self._source = rfile.read()

        self._alloc()
        self._compile()
        self._extract_links()

    def _extract_links(self):
        links = list(extract_links(self._source))
        self._attributes = set(lnk[1] for lnk in links if lnk[0] == KEYWORD_ATTRIBUTE)
        self._uniforms = set(lnk[1] for lnk in links if lnk[0] == KEYWORD_UNIFORM)

    @property
    def hnd(self):
        return self._hnd

    def _alloc(self):
        self._hnd = glCreateShader(self._kind)
        logging.info('glCreateShader(%s) -> %d', self._kind.name, self._hnd)
        if self._hnd == 0:
            raise ValueError('glCreateShader failed')

    def release(self, conn):
        if self._hnd is not None:
            conn.send_msg(lambda: glDeleteShader(self._hnd))

    def _compile(self):
        logging.info('glShaderSource(%d, ...)', self._hnd)
        glShaderSource(self._hnd, self._source)
        logging.info('glCompileShader(%d)', self._hnd)
        glCompileShader(self._hnd)

        if glGetShaderiv(self._hnd, GL_COMPILE_STATUS) is False:
            compile_log = glGetShaderInfoLog(self._hnd)
            glDeleteShader(self._hnd)
            raise RuntimeError('shader failed to compile', compile_log)

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
    def __init__(self):
        self._hnd = None
        self._shaders = []
        self._uniforms = {}
        self._attributes = {}
        self._alloc()

    def _alloc(self):
        self._hnd = glCreateProgram()
        logging.info('glCreateProgram() -> %d', self._hnd)
        if self._hnd == 0:
            raise ValueError('glCreateProgram failed')

    @contextmanager
    def bind(self):
        glUseProgram(self._hnd)
        try:
            yield
        finally:
            glUseProgram(0)

    def bind_attributes(self, buffer_objects, attribute_inputs):
        for attr_name, attr_index in self._attributes.items():
            data = attribute_inputs[attr_name]
            bufname = data['buffer']
            buf = buffer_objects[bufname]

            # TODO
            assert(data['gltype'] == 'float')
            gltype = GL_FLOAT
            buf.bind_to_attribute(attr_index,
                                  components=data['components'],
                                  gltype=gltype,
                                  normalized=data['normalized'],
                                  offset=data['offset'],
                                  stride=data['stride'])

    def bind_uniforms(self, uniforms):
        for uniform_name, uniform_index in self._uniforms.items():
            uniform = uniforms[uniform_name]
            uniform.bind(uniform_index)

    def update(self, msg):
        # TODO: for now this is just create, not really update
        for path in msg['vert_shader_paths']:
            self._shaders.append(VertexShader(path))
            
        for path in msg['frag_shader_paths']:
            self._shaders.append(FragmentShader(path))

        for shader in self._shaders:
            logging.info('glAttachShader(%d, %d)', self._hnd, shader.hnd)
            glAttachShader(self._hnd, shader.hnd)
        logging.info('glLinkProgram(%d)', self._hnd)
        glLinkProgram(self._hnd)

        self._uniforms = {}
        self._attributes = {}
        for shader in self._shaders:
            for name in shader.uniforms():
                self._uniforms[name] = glGetUniformLocation(self._hnd, name)
            for name in shader.attributes():
                self._attributes[name] = glGetAttribLocation(self._hnd, name)

    def alloc(self):
        hnd = glCreateProgram()
        logging.info('glCreateProgram() -> %d', hnd)
        if hnd == 0:
            raise ValueError('glCreateProgram failed')
        return hnd

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
