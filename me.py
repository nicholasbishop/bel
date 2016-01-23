#!/usr/bin/env python3

import pybliz
from pybliz import gl


def main():
    scene = pybliz.Scene()

    window = pybliz.Window(scene)
    window.run()

if __name__ == '__main__':
    main()
