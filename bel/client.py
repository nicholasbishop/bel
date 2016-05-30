from argparse import ArgumentParser
from asyncio import get_event_loop, open_unix_connection
from importlib import import_module
from logging import DEBUG, getLogger
from inspect import getmembers, ismethod

from bel.proctalk.rpc import JsonRpc
import bel.log


def create_peer_api(api):
    def init(self, rpc, client_id):
        self.rpc = rpc
        self.client_id = client_id

    def make_method(method_name):
        async def method(self, *params):
            return await self.rpc.call('_hub_dispatch', {
                'client_id': self.client_id,
                'method': method_name,
                'params': params
            })
        return method

    members = {'__init__': init}
    for method_name in api:
        members[method_name] = make_method(method_name)
    return type('PeerApi', (object,), members)


def expose(method):
    method.expose = True
    return method


class BaseClient:
    def __init__(self, log, event_loop, rpc, client_id):
        rpc.set_handler(self)
        self._log = log
        self._rpc = rpc
        self._running = True
        self._event_loop = event_loop
        self._client_id = client_id

    @property
    def rpc(self):
        return self._rpc

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, is_running):
        self._running = is_running

    def stop(self):
        self._log.info('BaseClient.stop() called')
        self._running = False
        self._rpc.stop()
        self._event_loop.stop()

    @expose
    def _identify(self):
        methods = []
        for method_name, method in getmembers(self, ismethod):
            if getattr(method, 'expose', False) is True:
                methods.append(method_name)
        return {
            'client_id': self._client_id,
            'methods': methods
        }

    @expose
    # TODO, better name
    def _tell_peers(self, peers):
        for client_id, methods in peers.items():
            if client_id != self._client_id:
                # TODO, formalize this better
                short_name = client_id.replace('_client', '')
                short_name = short_name.replace('bel.', '')
                short_name = short_name.replace('.', '-')
                self._log.debug('short_name=%s', short_name)
                peer_api = create_peer_api(methods)
                setattr(self, short_name, peer_api(self._rpc, client_id))

    @expose
    async def _shutdown(self):
        await self._rpc.call_ignore_result('shutdown')
        self.stop()

    def shutdown(self):
        self._event_loop.create_task(self._shutdown())


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

    # TODO: removing client_id from JsonRpc
    rpc = JsonRpc(cli_args.client_id, reader, writer)
    mod = import_module(cli_args.module)
    cls = getattr(mod, cli_args.cls)
    return cls(log, event_loop, rpc, cli_args.client_id)


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
