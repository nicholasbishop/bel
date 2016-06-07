#! /usr/bin/env python3

import logging

from bel import log
from bel.scene import Scene
from bel.window import Window

class Demo:
    def __init__(self):
        self._scene = Scene()
        self._window = Window()
        self._window.set_draw(self.draw)

    def run(self):
        self._window.run()

    def draw(self):
        scene.draw()


def main():
    log.configure('demo', logging.DEBUG)

    demo = Demo()
    demo.run()


if __name__ == '__main__':
    main()
