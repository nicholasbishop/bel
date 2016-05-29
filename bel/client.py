from argparse import ArgumentParser
from asyncio import get_event_loop, open_unix_connection
from importlib import import_module
from logging import DEBUG, getLogger

from bel.ipc import JsonRpc
import bel.log

class BaseClient:
    def __init__(self, log, event_loop, rpc):
        rpc.set_handler(self)
        self._log = log
        self._rpc = rpc
        self._running = True
        self._event_loop = event_loop

    @property
    def running(self):
        return self._running

    def stop(self):
        self._running = False
        self._rpc.stop()


def parse_args():
    """Parse command-line arguments."""
    parser = ArgumentParser()
    parser.add_argument('client_id')
    parser.add_argument('socket_path')
    parser.add_argument('module')
    parser.add_argument('cls')
    return parser.parse_args()


async def connect(log, event_loop, cli_args):
    reader, writer = await open_unix_connection(cli_args.socket_path)

    rpc = JsonRpc(cli_args.client_id, reader, writer)
    mod = import_module(cli_args.module)
    cls = getattr(mod, cli_args.cls)
    return cls(log, event_loop, rpc)


def main():
    args = parse_args()
    bel.log.configure(args.client_id, DEBUG)

    log = getLogger(__name__)
    log.info('client_id=%s, socket_path=%s, module=%s, cls=%s',
             args.client_id, args.socket_path, args.module, args.cls)

    event_loop = get_event_loop()
    event_loop.set_debug(True)
    client = event_loop.run_until_complete(connect(log, event_loop, args))
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass

    client.stop()
    event_loop.stop()
    event_loop.run_forever()
    event_loop.close()

    log.info('client %s exiting', args.client_id)


if __name__ == '__main__':
    main()
