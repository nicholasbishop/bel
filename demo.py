#! /usr/bin/env python3

from asyncio import get_event_loop
import logging

from bel.hub import Hub
from bel import log

def main():
    log.configure('demo', logging.DEBUG)

    get_event_loop().set_debug(True)

    hub = Hub()
    hub.launch_client('bel.glfw_client', 'GlfwClient')
    hub.run()


if __name__ == '__main__':
    main()
