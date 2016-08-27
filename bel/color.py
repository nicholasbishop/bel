from random import random as randfloat

import attr

@attr.s
class Color:
    red = attr.ib(default=0.0)
    green = attr.ib(default=0.0)
    blue = attr.ib(default=0.0)
    alpha = attr.ib(default=0.0)

    def as_tuple(self):
        return (self.red, self.green, self.blue, self.alpha)

    def serialize(self):
        return self.as_tuple()

    @classmethod
    def random(cls):
        return Color(randfloat(), randfloat(), randfloat(), 1.0)
