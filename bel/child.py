import asyncio
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
    reader, writer = await asyncio.open_unix_connection(socket_path)

    rpc = JsonRpc('child', reader, writer)
    handler = Handler(rpc)

    logging.info('child sleeping...')
    await asyncio.sleep(0.5)
    logging.info('child done sleeping')

    await rpc.send_request(None, 'shutdown', [])
    rpc.stop()
    # request = await rpc.read()
    # logging.info(request)

    # print('Send: %r' % message)
    # writer.write(message.encode())

    # data = yield from reader.read(100)
    # print('Received: %r' % data.decode())

    #await writer.drain()
    #writer.close()


def main():
    socket_path = sys.argv[1]
    logging.info('starting child, socket path: %s', socket_path)

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(child(socket_path))
    event_loop.run_forever()

    # reader = asyncio.StreamReader()
    # protocol_factory = lambda: asyncio.StreamReaderProtocol(reader)

    # async def connect_read():
    #     transport, protocol = await event_loop.connect_read_pipe(
    #         protocol_factory, sys.stdin)

    # event_loop.run_until_complete(connect_read())

    # def stdin_callback():
    #     reader = JsonStreamReader(transport)
    #     yield from reader.read()
    #     event_loop.stop()

    
    # #event_loop.add_reader(sys.stdin.fileno(), stdin_callback)

    # event_loop.run_until_complete(stdin_callback())

    # event_loop.run_forever()
    

    # #print('the end:', out)

    # event_loop.close()
    logging.info('child finished')
    

if __name__ == '__main__':
    log.configure('child', logging.DEBUG)
    main()
