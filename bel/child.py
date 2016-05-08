from logging import debug, DEBUG
from sys import argv

from bel import log
from bel.ipc import Conn

def main(name, then):
    log.configure(name, DEBUG)
    debug('child main: %s', name)
    socket_path = argv[1]
    conn = Conn.connect(socket_path)
    # TODO(nicholasbishop): might change this to a class
    debug('entering individual child code')
    then(conn)
    debug('child exiting')
