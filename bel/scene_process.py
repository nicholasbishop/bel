from enum import Enum
import logging

from bel.child import main
from bel.msg import Msg, Tag


class Dirty(Enum):
    BackgroundColor = 1


class Scene:
    def __init__(self, conn):
        self._background_color = (0.3, 0.3, 0.4, 0.0)
        self._conn = conn
        self._dirty = set((Dirty.BackgroundColor,))
        self._event_handlers = {}

    def _mark_dirty(self, dirty):
        self._dirty.add(dirty)

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self._mark_dirty(Dirty.BackgroundColor)
        # TODO, second thread
        self._conn.send_msg(Msg(Tag.WND_SetClearColor,
                                self._background_color))

    def event_mouse_button(self, event):
        handler = self._event_handlers.get('mouse_button')
        if handler is not None:
            handler(self, event)

    def attach_event_handler(self, event_type, handler):
        # TODO, multiple handlers for same event type
        self._event_handlers[event_type] = handler


def scene_main(conn):
    scene = Scene(conn)
    running = True
    while running:
        # TODO: timeout?
        messages = conn.read_messages_blocking()
        for msg in messages:
            if msg.tag == Tag.Exit:
                running = False
            elif msg.tag == Tag.SCE_SetBackgroundColor:
                scene.background_color = msg.body
            elif msg.tag == Tag.SCE_AttachEventHandler:
                # TODO, formalize message bodies
                scene.attach_event_handler(*msg.body)
            elif msg.tag == Tag.SCE_EventMouseButton:
                scene.event_mouse_button(msg.body)

if __name__ == '__main__':
    main('sce', scene_main)
