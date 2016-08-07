from collections import OrderedDict
from contextlib import contextmanager
from copy import deepcopy
from enum import Enum, unique

EMPTY_LINE = ''

@unique
class Storage(Enum):
    Input = 'in'
    Output = 'out'

class Expr(object):
    def __mul__(self, other):
        return MulOp(self, other)


class StructAccess(Expr):
    def __init__(self, struct, field):
        self.struct = struct
        self.field = field


class Struct(object):
    def __init__(self, name):
        self.name = name

    def __getattr__(self, name):
        return StructAccess(self, name)


class GeomIn(Struct):
    def __init__(self):
        super().__init__('gl_PerVertex')
        self.gl_Position = StructField('gl_Position')
        # TODO(nicholasbishop):
        # float gl_PointSize;
        # float gl_ClipDistance[];



class FunctionCall(Expr):
    def __init__(self, function, args):
        self.function = function
        self.args = args


class Function(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, *args):
        return FunctionCall(self, args)


class GlslVar(Expr):
    @classmethod
    def keyword(cls):
        return cls.__name__.lower()

    def __init__(self, *args):
        self._args = args
        self.name = None

    def constructor_args(self):
        for arg in self._args:
            if isinstance(arg, Attribute):
                yield arg.input_name
            elif isinstance(arg, (float, int)):
                yield str(arg)
            else:
                raise NotImplementedError(arg)

    def expr_code(self):
        if self.name is None:
            # Lack of name indicates this is a temporary value
            return '{}({})'.format(self.keyword(),
                                   ', '.join(self.constructor_args()))
        else:
            return self.name


class ArrayGet(Expr):
    def __init__(self, array, index):
        self.array = array
        self.index = index

    def __getattr__(self, name):
        return StructAccess(self.array.base_type, name)


class ArraySet(Expr):
    def __init__(self, array, index, value):
        self.array = array
        self.index = index
        self.value = value


class Array(GlslVar):
    def __init__(self, base_type, *shape):
        self.base_type = base_type
        self.shape = shape

    def __getitem__(self, index):
        return ArrayGet(self, index)

    def __setitem__(self, index, value):
        return ArraySet(self, index, value)


class BuiltinArray(Array):
    pass


class Vec2(BuiltinArray):
    pass

class Vec3(BuiltinArray):
    pass

class Vec4(BuiltinArray):
    pass

class Mat4(BuiltinArray):
    pass


class BinaryOp(Expr):
    def __init__(self, operator, lop, rop):
        self._operator = operator
        self._lop = lop
        self._rop = rop

    def expr_code(self):
        return '({} {} {})'.format(self._lop.expr_code(),
                                   self._operator,
                                   self._rop.expr_code())


class MulOp(BinaryOp):
    def __init__(self, lop, rop):
        super().__init__('*', lop, rop)


class Uniform(Expr):
    def __init__(self, glsl_var):
        self.glsl_var = glsl_var
        self.name = None

    def expr_code(self):
        return self.name

    def decl(self):
        return 'uniform {} {};'.format(self.glsl_var.keyword(), self.name)


class Attribute(Expr):
    def __init__(self, glsl_var, input_name=None, output_name=None,
                 no_perspective=False):
        self.glsl_var = glsl_var
        self._input_name = input_name
        self._output_name = output_name
        self._no_perspective = no_perspective

    def __repr__(self):
        return 'Attribute({}, in={}, out={})'.format(
            self.glsl_var.keyword(),
            self._input_name,
            self._output_name)

    def __getitem__(self, index):
        return self.glsl_var[index]

    def is_builtin(self):
        name = self._output_name
        return (name is not None) and name.startswith('gl_')

    @property
    def input_name(self):
        if self._input_name is None:
            raise ValueError('invalid input name')
        return self._input_name

    @input_name.setter
    def input_name(self, name):
        self._input_name = name

    @property
    def output_name(self):
        if self._output_name is None:
            raise ValueError('invalid output name')
        return self._output_name

    @output_name.setter
    def output_name(self, name):
        self._output_name = name

    def decl(self, storage):
        parts = []
        if self._no_perspective is True:
            parts.append('noperspective')

        parts += [storage.value, self.glsl_var.keyword()]

        if storage == Storage.Input:
            parts.append(self.input_name)
        elif storage == Storage.Output:
            parts.append(self.output_name)

        return ' '.join(parts)


class Scope:
    def __init__(self):
        self._vars = []

    def __setattr__(self, name, value):
        if name.startswith('_'):
            # Ignore private members
            super().__setattr__(name, value)
        else:
            self._vars[name] = value


class GeomScope(Scope):
    def __init__(self):
        super().__init__()

    def emit_vertex(self, **kwargs):
        # TODO
        pass
        

class Material(object):
    def __init__(self):
        self.gl_Position = None  # pylint: disable=invalid-name
        self._capture = False
        self._exprs = OrderedDict()

    def __setattr__(self, key, val):
        private = key.startswith('_')
        capturing = getattr(self, '_capture', False)
        if capturing and not private:
            self._exprs[key] = val
        else:
            super().__setattr__(key, val)

    def captured_expressions(self):
        return self._exprs

    @contextmanager
    def capture(self):
        self._capture = True
        yield
        self._capture = False

    def _members_of_type(self, target_type):
        for attr_name in sorted(dir(self)):
            attr_val = getattr(self, attr_name)
            if isinstance(attr_val, target_type):
                yield attr_name, attr_val

    def apply_names(self, input_prefix, output_prefix):
        for name, uniform in self._members_of_type(Uniform):
            uniform.name = name

        for name, attr in self._members_of_type(Attribute):
            attr.input_name = input_prefix + name
            attr.output_name = output_prefix + name

    def uniforms(self):
        for _, uniform in self._members_of_type(Uniform):
            yield uniform

    def attributes(self):
        for _, attr in self._members_of_type(Attribute):
            yield attr

    def find_attribute(self, name):
        return dict(self._members_of_type(Attribute))[name]

    def generate_vert_shader(self):
        vert_shader = deepcopy(self)
        vert_shader.apply_names('', 'vs_')
        vert_shader.gl_Position = Attribute(Vec4, output_name='gl_Position')
        with vert_shader.capture():
            vert_shader.vert()

        yield '#version 330 core'
        yield EMPTY_LINE

        for uniform in vert_shader.uniforms():
            yield uniform.decl()

        yield EMPTY_LINE

        # TODO, dep-res needed for usage analysis and ordering of
        # expressions

        for attr in vert_shader.attributes():
            if not attr.is_builtin():
                yield attr.decl(Storage.Input)

        yield EMPTY_LINE

        for attr in vert_shader.attributes():
            yield attr.decl(Storage.Output)

        yield EMPTY_LINE

        exprs = vert_shader.captured_expressions()
        finished_attrs = []

        yield 'void main() {'
        for name, expr in exprs.items():
            # TODO, handle named local vars?
            attr = vert_shader.find_attribute(name)
            finished_attrs.append(attr)
            # TODO
            yield '    {} = {};'.format(attr.output_name,
                                        expr.expr_code())

        # TODO, another case where dep-res is needed
        for attr in vert_shader.attributes():
            if attr not in finished_attrs:
                # TODO, de-dup
                print(attr)
                yield '    {} = {};'.format(attr.output_name,
                                            attr.input_name)

        yield '}'

    # TODO, de-dup
    def generate_geom_shader(self):
        geom_shader = deepcopy(self)
        geom_shader.apply_names('vs_', 'gs_')
        geom_shader.gl_in = Attribute(Array(GeomIn), input_name='gl_in')
        output = GeomScope()
        with geom_shader.capture():
            geom_shader.geom(output)
        yield EMPTY_LINE


def perspective_project(projection, camera, model, point):
    return projection * camera * model * point


viewport_to_screen_space = Function('viewport_to_screen_space')
triangle_2d_altitudes = Function('triangle_2d_altitudes')


class DefaultMaterial(Material):
    def __init__(self):
        super().__init__()
        self.projection = Uniform(Mat4)
        self.camera = Uniform(Mat4)
        self.model = Uniform(Mat4)
        self.framebuffer_size = Uniform(Vec2)
        self.vert_loc = Attribute(Vec3)
        self.vert_nor = Attribute(Vec3)
        self.vert_col = Attribute(Vec4)

    def vert(self):
        self.gl_Position = perspective_project(self.projection,
                                               self.camera,
                                               self.model,
                                               Vec4(self.vert_loc, 1.0))

    def geom(self, output):
        triangle = Array(Vec2, 3)
        for index in range(3):
            triangle[index] = viewport_to_screen_space(
                self.framebuffer_size,
                self.gl_in[index].gl_Position)

        altitudes = Vec3(triangle_2d_altitudes(triangle))

        output.emit_vertex(
            altitude=Vec3(altitudes[0], 0, 0)
        )


def main():
    default = DefaultMaterial()
    print('\n'.join(default.generate_vert_shader()))
    print('\n'.join(default.generate_geom_shader()))

main()
