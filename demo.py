#! /usr/bin/env python3

import asyncio
import json
import logging
import os
from tempfile import TemporaryDirectory
import sys

from bel.ipc import JsonRpc
from bel import log


class Handler:
    def __init__(self, rpc):
        rpc.set_handler(self)
        self._rpc = rpc

    async def shutdown(self):
        logging.info('hub: shutdown received')
        self._rpc.stop()
        asyncio.get_event_loop().stop()


async def client_connected(reader, writer):
    logging.info('child connected')

    rpc = JsonRpc('demo', reader, writer)
    handler = Handler(rpc)

    def receive_hello(result):
        logging.info('hub: received method response: %r', result)

    await rpc.send_request(receive_hello, 'hello_from_hub', [])


async def run_hub(socket_path):
    server = await asyncio.start_unix_server(client_connected, socket_path)
    return server


async def start_children(socket_path):
    cmd = (sys.executable, '-m', 'bel.child', socket_path)
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.wait()


def main():
    with TemporaryDirectory(prefix='bel-') as temp_dir:
        socket_path = os.path.join(temp_dir, 'bel.socket')
        logging.info('socket path: %s', socket_path)

        event_loop = asyncio.get_event_loop()
        server_task = event_loop.create_task(run_hub(socket_path))
        event_loop.create_task(start_children(socket_path))
        try:
            event_loop.run_forever()
        except KeyboardInterrupt:
            pass

        server = server_task.result()
        server.close()
        event_loop.run_until_complete(server.wait_closed())
        event_loop.close()
    

if __name__ == '__main__':
    # TODO
    #asyncio.get_event_loop().set_debug(True)

    log.configure('demo', logging.DEBUG)
    from bel.hub import Hub
    hub = Hub()
    hub.launch_client('child')
    hub.run()

    asyncio.get_event_loop().close()
    
    #main()
