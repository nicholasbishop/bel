#!/usr/bin/env python3

import pybliz


def main():
    scene = pybliz.SceneNode()
    geom = pybliz.MeshNode()
    scene.add(geom)

    window = pybliz.Window(scene)
    window.run()

if __name__ == '__main__':
    main()
