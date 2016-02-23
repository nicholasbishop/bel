from OpenGL import GL as gl
from pybliz.math3d import *

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
        self._hnd = gl.glCreateShader(kind)
        if self._hnd == 0:
            raise ValueError('glCreateShader failed')
        with open(path) as rfile:
            source = rfile.read()
            gl.glShaderSource(self._hnd, source)
        gl.glCompileShader(self._hnd)
        if gl.glGetShaderiv(self._hnd, gl.GL_COMPILE_STATUS) == False:
            log = gl.glGetShaderInfoLog(self._hnd)
            gl.glDeleteShader(self._hnd)
            raise RuntimeError('shader failed to compile', log)
        links = list(extract_links(source))
        self._attributes = set(lnk[1] for lnk in links if lnk[0] == KEYWORD_ATTRIBUTE)
        self._uniforms = set(lnk[1] for lnk in links if lnk[0] == KEYWORD_UNIFORM)

    def uniforms(self):
        return self._uniforms

    def attributes(self):
        return self._attributes


class VertexShader(Shader):
    def __init__(self, path):
        super().__init__(path, gl.GL_VERTEX_SHADER)


class FragmentShader(Shader):
    def __init__(self, path):
        super().__init__(path, gl.GL_FRAGMENT_SHADER)


class Program:
    def __init__(self, vertex_shader, fragment_shader):
        self._vs = vertex_shader
        self._fs = fragment_shader
        self._hnd = gl.glCreateProgram()
        if self._hnd == 0:
            raise ValueError('glCreateProgram failed')
        gl.glAttachShader(self._hnd, self._vs._hnd)
        gl.glAttachShader(self._hnd, self._fs._hnd)
        gl.glLinkProgram(self._hnd)
        self._uniforms = {}
        self._attributes = {}
        for name in self._vs.uniforms() | self._fs.uniforms():
            self._uniforms[name] = gl.glGetUniformLocation(self._hnd, name)
        for name in self._vs.attributes() | self._fs.attributes():
            self._attributes[name] = gl.glGetAttribLocation(self._hnd, name)

    def bind(self):
        gl.glUseProgram(self._hnd)

    def set_uniform(self, key, val):
        loc = self._uniforms[key]
        if isinstance(val, Mat4x4):
            gl.glUniformMatrix4fv(loc, 1, False, val._dat.flatten(order='F'))

    def get_attribute_location(self, key):
        return self._attributes[key]
