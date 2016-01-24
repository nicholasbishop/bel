#!/usr/bin/env python3

import pybliz


def main():
    window = pybliz.Window()
    scene = window.scene()
    mesh = pybliz.MeshNode.load_obj('examples/cube.obj')
    scene.add(mesh)
    window.run()

if __name__ == '__main__':
    main()
