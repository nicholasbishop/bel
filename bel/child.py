from asyncio import get_event_loop, open_unix_connection, sleep
import logging
import sys

from bel.ipc import JsonRpc
from bel import log

class Handler:
    def __init__(self, rpc):
        rpc.set_handler(self)
        self._rpc = rpc

    async def hello_from_hub(self, *args, **kwargs):
        logging.info('hello received')
        return 'and hello from child!'


async def child(socket_path):
    reader, writer = await open_unix_connection(socket_path)

    rpc = JsonRpc('child', reader, writer)
    handler = Handler(rpc)

    logging.info('child sleeping...')
    await sleep(0.5)
    logging.info('child done sleeping')

    await rpc.send_request(None, 'shutdown')
    rpc.stop()

def main():
    socket_path = sys.argv[1]
    logging.info('starting child, socket path: %s', socket_path)

    event_loop = get_event_loop()
    event_loop.run_until_complete(child(socket_path))
    event_loop.stop()
    event_loop.close()

    logging.info('child finished')
    

if __name__ == '__main__':
    log.configure('child', logging.DEBUG)
    main()
