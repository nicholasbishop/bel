from random import random as randfloat

class Color:
    def __init__(self, r=0.0, g=0.0, b=0.0, a=0.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @classmethod
    def random(cls):
        return Color(randfloat(), randfloat(), randfloat(), 1.0)
