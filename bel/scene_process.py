from enum import Enum

from bel.child import main
from bel.msg import Tag


class Dirty(Enum):
    BackgroundColor = 1


class Scene:
    def __init__(self, conn):
        self._background_color = (1, 0, 0)
        self._conn = conn

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self._mark_dirty(Dirty.BackgroundColor)
        # TODO, second thread
        self._conn.send_msg(Msg(Tag.SetClearColor, self._background_color))


def scene_main(conn):
    scene = Scene(conn)
    running = True
    while running:
        # TODO: timeout?
        msg = conn.read_msg_blocking()
        if msg.tag == Tag.Exit:
            running = False
        elif msg.tag == Tag.SetBackgroundColor:
            scene.background_color = msg.body

if __name__ == '__main__':
    main('sce', scene_main)
