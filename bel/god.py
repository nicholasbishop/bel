#! /usr/bin/env python

import logging

from bel import log
from bel.hub import Hub
from bel.msg import Msg, Tag


def mouse_button_handler(scene, event):
    from random import random
    scene.background_color = (
        random(),
        random(),
        random(),
        0.0
    )


def main():
    hub = Hub()
    hub.start_background_thread()
    hub.send_msg(Msg(Tag.SCE_AttachEventHandler, ('mouse_button',
                     mouse_button_handler)))
    hub.join_background_thread()


if __name__ == '__main__':
    log.configure('god', logging.DEBUG)
    main()
