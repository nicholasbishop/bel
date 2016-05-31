from collections.abc import Mapping
from inspect import signature, Parameter
from unittest import TestCase

from bel.color import Color


def deserialize(argument, parameter):
    if parameter.annotation != Parameter.empty:
        method = getattr(parameter.annotation, 'deserialize', None)
        if method is not None:
            return method(argument)
    # Fall back to the unmodified argument
    return argument


def deserialize_list_args(func, args):
    sig = signature(func)
    if len(sig.parameters) != len(args):
        raise ValueError('signature does not match inputs')
    return [deserialize(arg, param)
            for arg, param
            in zip(args, sig.parameters.values())]


def deserialize_dict_args(func, args):
    return args


def deserialize_and_call(func, args):
    if args is None:
        return func()
    elif isinstance(args, Mapping):
        return func(**deserialize_dict_args(func, args))
    else:
        return func(*deserialize_list_args(func, args))


class TypeTransTest(TestCase):
    def test_list(self):
        def func(color1: Color):
            return color1
        args = deserialize_list_args(func, [[0, 0, 0, 0]])
        self.assertEqual(args, [Color(0, 0, 0, 0)])
