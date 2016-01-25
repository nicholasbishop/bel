from OpenGL import GL as gl
from pybliz.math3d import *

def extract_uniforms(source):
    for line in source.splitlines():
        parts = line.split()
        if len(parts) > 0 and parts[0] == 'uniform':
            yield parts[2].rstrip(';')


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
        self._uniforms = set(extract_uniforms(source))

    def uniforms(self):
        return self._uniforms


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
        for name in self._vs.uniforms() | self._fs.uniforms():
            self._uniforms[name] = gl.glGetUniformLocation(self._hnd, name)

    def bind(self):
        gl.glUseProgram(self._hnd)

    def set_uniform(self, key, val):
        loc = self._uniforms[key]
        if isinstance(val, Mat4x4):
            gl.glUniformMatrix4fv(loc, 1, False, val._array)
