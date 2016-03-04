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
        self._uid = None
        with open(self._path) as rfile:
            self._source = rfile.read()

    def extract_links(self):
        links = list(extract_links(self.source))
        self._attributes = set(lnk[1] for lnk in links if lnk[0] == KEYWORD_ATTRIBUTE)
        self._uniforms = set(lnk[1] for lnk in links if lnk[0] == KEYWORD_UNIFORM)

    @property
    def uid(self):
        return self._uid

    def alloc(self):
        hnd = glCreateShader(self._kind)
        logging.info('glCreateShader(%s) -> %d', self._kind.name, hnd)
        if hnd == 0:
            raise ValueError('glCreateShader failed')
        return hnd

    def release(self, conn):
        if self._hnd is not None:
            conn.send_msg(lambda: glDeleteShader(self._hnd))

    def compile(self, hnd):
        logging.info('glShaderSource(%d, ...)', hnd)
        glShaderSource(hnd, self._source)
        logging.info('glCompileShader(%d)', hnd)
        glCompileShader(hnd)

        if glGetShaderiv(hnd, GL_COMPILE_STATUS) is False:
            compile_log = glGetShaderInfoLog(hnd)
            glDeleteShader(hnd)
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
    def __init__(self, uid):
        self._shaders = []
        self._uid = uid
        self._next_shader_suffix = 0
        self._finalized = False

    @property
    def uid(self):
        return self._uid

    def _take_shader_uid(self):
        shader_uid = '{}.{}'.format(self._uid, self._next_shader_suffix)
        self._next_shader_suffix += 1
        return shader_uid

    def add_vert_shader_from_path(self, path):
        shader = VertexShader(path)
        shader._uid = self._take_shader_uid()
        self._shaders.append(shader)

    def add_frag_shader_from_path(self, path):
        shader = FragmentShader(path)
        shader._uid = self._take_shader_uid()
        self._shaders.append(shader)

    def finalize(self, conn):
        if self._finalized:
            raise RuntimeError('already finalized')

        def async(resources):
            for shader in self._shaders:
                if shader.uid not in resources:
                    resources[shader.uid] = shader.alloc()
                shader.compile(resources[shader.uid])

            if self.uid not in resources:
                resources[self.uid] = self.alloc()

            rprog = resources[self.uid]
            for shader in self._shaders:
                rshad = resources[shader.uid]
                logging.info('glAttachShader(%d, %d)', rprog, rshad)
                glAttachShader(rprog, rshad)
            logging.info('glLinkProgram(%d)', rprog)
            glLinkProgram(rprog)

        self._finalized = True
        conn.send_msg(async)


        # TODO!
        # self._uniforms = {}
        # self._attributes = {}
        # for name in self._vert_shader.uniforms() | self._frag_shader.uniforms():
        #     self._uniforms[name] = glGetUniformLocation(self._hnd, name)
        # for name in self._vert_shader.attributes() | self._frag_shader.attributes():
        #     self._attributes[name] = glGetAttribLocation(self._hnd, name)

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
