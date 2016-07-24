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
            elif isinstance(arg, float):
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


class Vec3(GlslVar):
    pass


class Vec4(GlslVar):
    pass

class Mat4(GlslVar):
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
    def __init__(self, glsl_type):
        self.glsl_type = glsl_type
        self.name = None

    def expr_code(self):
        return self.name

    def decl(self):
        return 'uniform {} {};'.format(self.glsl_type.keyword(), self.name)


class Attribute(Expr):
    def __init__(self, glsl_type, output_name=None):
        self.glsl_type = glsl_type
        self._input_name = None
        self._output_name = output_name

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
        if storage == Storage.Input:
            name = self.input_name
        elif storage == Storage.Output:
            name = self.output_name
        return '{} {} {};'.format(storage.value,
                                  self.glsl_type.keyword(),
                                  name)


class Material(object):
    def __init__(self):
        # pylint: disable=invalid-name
        self.gl_Position = None

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

    def exprs(self):
        for name, attr in self._members_of_type(Expr):
            if isinstance(attr, Attribute):
                continue
            if isinstance(attr, Uniform):
                continue
            yield name, attr

    def generate_vert_shader(self):
        vert_shader = deepcopy(self)
        vert_shader.apply_names('', 'vs_')
        vert_shader.vert()

        yield '#version 330 core'
        yield EMPTY_LINE

        for uniform in vert_shader.uniforms():
            yield uniform.decl()

        yield EMPTY_LINE

        # TODO, dep-res

        for attr in vert_shader.attributes():
            yield attr.decl(Storage.Input)

        yield EMPTY_LINE

        for attr in vert_shader.attributes():
            yield attr.decl(Storage.Output)

        yield EMPTY_LINE

        yield 'void main() {'
        for name, expr in vert_shader.exprs():
            # TODO
            yield '    {} = {};'.format(name, expr.expr_code())
        yield '}'


def perspective_project(projection, camera, model, point):
    return projection * camera * model * point


class DefaultMaterial(Material):
    def __init__(self):
        super().__init__()
        self.projection = Uniform(Mat4)
        self.camera = Uniform(Mat4)
        self.model = Uniform(Mat4)
        self.vert_loc = Attribute(Vec3)
        self.vert_nor = Attribute(Vec3)
        self.vert_col = Attribute(Vec4)

    def vert(self):
        self.gl_Position = perspective_project(self.projection,
                                               self.camera,
                                               self.model,
                                               Vec4(self.vert_loc, 1.0))

def main():
    default = DefaultMaterial()
    print('\n'.join(default.generate_vert_shader()))

main()
