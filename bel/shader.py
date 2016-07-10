from contextlib import contextmanager
import logging
import re

from bidict import bidict

from OpenGL.GL import (GL_COMPILE_STATUS, GL_FLOAT,
                       GL_FRAGMENT_SHADER, GL_GEOMETRY_SHADER,
                       GL_VERTEX_SHADER, glAttachShader,
                       glCompileShader, glCreateProgram,
                       glCreateShader, glDeleteShader,
                       glEnableVertexAttribArray, glGetProgramInfoLog,
                       glGetUniformLocation, glGetShaderInfoLog,
                       glGetShaderiv, glLinkProgram, glShaderSource,
                       glUseProgram)

KEYWORD_ATTRIBUTE = 'attribute'
KEYWORD_UNIFORM = 'uniform'


# TODO, this is just what works for my driver
def pretty_print_log(log, path):
    # Example input line:
    # 0:17(24): error: `gl_PositionIn' undeclared
    #
    # Example output line:
    # shaders/geom.glsl:17:24: error: `gl_PositionIn' undeclared

    print(re.sub(r'^(\d+):(\d+)\((\d+)\)',
                 path + r':\2:\3',
                 log,
                 flags=re.MULTILINE))


def extract_uniforms(source):
    for line in source.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] == 'uniform':
            name = parts[2].rstrip(';')
            yield name


def extract_links(source, keyword):
    for line in source.splitlines():
        parts = line.split()
        if (len(parts) >= 4 and parts[-3] == keyword and
                parts[0].startswith('layout')):
            layout = ''.join(parts[0:-3])
            layout = layout.replace('\t', '')
            layout = layout.replace(' ', '')
            index = layout.find('location=')
            if index != -1:
                index += len('location=')
                location = layout[index:-1]
                name = parts[-1][:-1]
                yield name, int(location)


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
        # TODO
        if self._kind == GL_VERTEX_SHADER:
            self._attributes = extract_links(self._source, 'in')
        self._uniforms = extract_uniforms(self._source)

    @property
    def hnd(self):
        return self._hnd

    def _alloc(self):
        # pylint: disable=assignment-from-no-return
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

        if not glGetShaderiv(self._hnd, GL_COMPILE_STATUS):
            logging.error('glCompileShader failed')
            compile_log = glGetShaderInfoLog(self._hnd).decode('utf-8')

            glDeleteShader(self._hnd)

            pretty_print_log(compile_log, self._path)

            raise RuntimeError('shader failed to compile', compile_log)

    def uniforms(self):
        return self._uniforms

    def attributes(self):
        return self._attributes


class VertexShader(Shader):
    def __init__(self, path):
        super().__init__(path, GL_VERTEX_SHADER)


class GeometryShader(Shader):
    def __init__(self, path):
        super().__init__(path, GL_GEOMETRY_SHADER)


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
        # pylint: disable=assignment-from-no-return
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
            pass#glUseProgram(0)

    def bind_attributes(self, buffer_objects, attribute_inputs):
        # TODO
        for attr_name, attr_index in self._attributes.items():
            data = attribute_inputs[attr_name]
            bufname = data['buffer']
            buf = buffer_objects[bufname]

            with buf.bind():
                glEnableVertexAttribArray(attr_index)
            # TODO
            buf.bind_to_attribute(attr_index,
                                  data['buffer_view'])

    def bind_uniforms(self, uniforms):
        for uniform_name, uniform_index in self._uniforms.items():
            uniform = uniforms[uniform_name]
            if uniform is None:
                raise KeyError(uniform_name)
            else:
                uniform.bind(uniform_index)

    def update(self, *shaders):
        # TODO: for now this is actually create, not update
        self._shaders += shaders

        for shader in self._shaders:
            logging.info('glAttachShader(%d, %d)', self._hnd, shader.hnd)
            glAttachShader(self._hnd, shader.hnd)
        logging.info('glLinkProgram(%d)', self._hnd)
        glLinkProgram(self._hnd)
        logging.info('glGetProgramInfoLog(%d) -> %s', self._hnd,
                     glGetProgramInfoLog(self._hnd).decode().strip())

        self._uniforms = {}
        self._attributes = bidict()
        for shader in self._shaders:
            for name in shader.uniforms():
                self._uniforms[name] = glGetUniformLocation(self._hnd, name)
                logging.info('glGetUniformLocation(%d, "%s") -> %d',
                             self._hnd, name, self._uniforms[name])
            for name, location in shader.attributes():
                if location in self._attributes.inv:
                    raise KeyError('duplication attribute location', location,
                                   name)
                self._attributes[name] = location

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
