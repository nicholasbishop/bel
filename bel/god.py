#! /usr/bin/env python

import logging

from bel import log
from bel.hub import Hub
from bel.msg import Msg, Tag

def main():
    hub = Hub()
    hub.start_background_thread()
    from time import sleep
    sleep(1)
    hub.send_msg(Msg(Tag.SCE_SetBackgroundColor, (0, 1, 0, 0)))
    hub.join_background_thread()


if __name__ == '__main__':
    log.configure('god', logging.DEBUG)
    main()
