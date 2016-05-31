from random import random as randfloat

class Color:
    def __init__(self, red=0.0, green=0.0, blue=0.0, alpha=0.0):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def __eq__(self, them):
        return (self.red == them.red and
                self.green == them.green and
                self.blue == them.blue and
                self.alpha == them.alpha)

    def as_tuple(self):
        return (self.red, self.green, self.blue, self.alpha)

    def serialize(self):
        return self.as_tuple()

    @classmethod
    def deserialize(cls, seq):
        return cls(*seq)

    @classmethod
    def random(cls):
        return Color(randfloat(), randfloat(), randfloat(), 1.0)
