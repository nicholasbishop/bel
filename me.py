#!/usr/bin/env python3

import pybliz


def main():
    window = pybliz.Window()
    mesh = pybliz.MeshNode.load_obj('examples/cube.obj')
    s = 0.8
    mesh.transform.set_scale(s, s, s)
    mesh.transform.set_translation(0, 0, -5)
    window.root.add(mesh)
    window.run()

if __name__ == '__main__':
    main()
