#! /usr/bin/env python3

import logging

from bel.hub import Hub
from bel import log

def main():
    log.configure('demo', logging.DEBUG)

    # TODO
    if False:
        from asyncio import get_event_loop
        get_event_loop().set_debug(True)

    hub = Hub()
    hub.launch_client('child')
    hub.run()


if __name__ == '__main__':
    main()
