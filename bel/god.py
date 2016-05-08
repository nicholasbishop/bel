#! /usr/bin/env python

import logging

from bel import ipc
from bel.hub import Hub
from bel import log

class Reader:
    def feed(self, data):
        print('received:', data)
        

def main():
    # proc = ipc.LaunchProcess('window', Reader())
    # proc.send_msg({
    #     'tag': 'exit'
    # })
    hub = Hub()
    hub.launch_children()
    hub.run_until_exit()


if __name__ == '__main__':
    log.configure('god', logging.DEBUG)
    main()
