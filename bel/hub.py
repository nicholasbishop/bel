from asyncio import (Event, create_subprocess_exec, get_event_loop,
                     start_unix_server)
from logging import getLogger
import os
import sys
from tempfile import TemporaryDirectory

from bel.proctalk.rpc import JsonRpc, expose

def _create_socket_dir():
    return TemporaryDirectory(prefix='bel-')


class Dispatcher:
    def __init__(self):
        pass


class Client:
    def __init__(self, hub, client_id, proc_task):
        proc_task.add_done_callback(self._proc_exited)

        self._client_id = client_id
        self._proc_task = proc_task
        self._hub = hub
        self._rpc = None
        self._methods = None

    @property
    def methods(self):
        return self._methods

    @property
    def client_id(self):
        return self._client_id

    def _proc_exited(self, task):
        pass #self._hub.client_exited(self, task)

    @property
    def rpc(self):
        return self._rpc

    async def get_proc(self):
        return await self._proc_task

    def connect(self, hub, rpc, methods):
        self._hub = hub
        self._rpc = rpc
        self._rpc.set_handler(self)
        self._methods = methods

    @expose
    async def _hub_dispatch(self, dct):
        dst = dct['dst']
        method = dct['method']
        params = dct['params']

        client = self._hub.get_client(dst)
        return await client.rpc.call(method, params)

    @expose
    async def shutdown(self):
        self._rpc.stop()
        self._rpc = None
        self._hub.event_loop.create_task(self._hub.shutdown())
        self._hub = None


class Hub:
    def __init__(self, event_loop=None):
        self._log = getLogger(__name__)
        self._event_loop = event_loop or get_event_loop()
        self._socket_path = None
        self._clients = {}
        self._server_task = None
        self._all_clients_connected = Event()

    def get_client(self, client_id):
        return self._clients[client_id]

    @property
    def event_loop(self):
        return self._event_loop

    def client_exited(self, client, task):
        # TODO, handle in some way...
        self._log.info('client %s exited: %r', client.client_id, task.result())

    def _check_all_clients_connected(self):
        self._log.debug('checking clients for connection...')
        for client in self._clients.values():
            if client.rpc is None:
                self._log.debug('client %s has not connected yet', client.client_id)
                return
        self._log.info('all clients (%d) have connected', len(self._clients))
        self._all_clients_connected.set()

    async def _identify_client(self, rpc):
        dct = await rpc.call('_identify')
        client_id = dct['client_id']
        methods = dct['methods']
        self._log.info('identity: %s', client_id)
        if client_id in self._clients:
            self._clients[client_id].connect(self, rpc, methods)
        else:
            self._log.error('unknown client: %s', client_id)
        self._check_all_clients_connected()

    def _on_client_connect(self, reader, writer):
        self._log.info('client connected')
        rpc = JsonRpc('hub', reader, writer, self._event_loop, self._log)
        self._event_loop.create_task(self._identify_client(rpc))

    def _create_server_task(self, socket_path):
        start_server = start_unix_server(self._on_client_connect, socket_path)
        return self._event_loop.create_task(start_server)

    async def shutdown(self):
        self._log.info('shutdown')
        if self._server_task:
            server = self._server_task.result()
            server.close()
            await server.wait_closed()
            self._server_task = None
        for client in self._clients.values():
            if client.rpc:
                try:
                    await client.rpc.call_ignore_result('_shutdown')
                except ConnectionResetError:
                    # Client has already disconnected
                    pass
                client.rpc.stop()
            proc = await client.get_proc()
            await proc.wait()
        self._event_loop.stop()

    async def _run_client(self, client_id, module, cls):
        cmd = [sys.executable, '-m', 'bel.client',
               client_id, self._socket_path, module, cls]
        # TODO
        use_gdb = False
        use_valgrind = False
        if use_gdb:
            cmd = ['gdb', '--args'] + cmd
        elif use_valgrind:
            cmd = ['valgrind'] + cmd
        proc = await create_subprocess_exec(*cmd)
        return proc

    def launch_client(self, module, cls):
        self._log.info('launch client')
        # TODO
        client_id = module
        if client_id in self._clients:
            raise KeyError('client already exists', client_id)
        else:
            proc_task = self._event_loop.create_task(self._run_client(client_id, module, cls))
            self._clients[module] = Client(self, client_id, proc_task)

    async def _broadcast_ignore_result(self, method, *params):
        for client in self._clients.values():
            await client.rpc.call_ignore_result(method, *params)

    async def _send_start_event(self):
        await self._all_clients_connected.wait()

        peers = {}
        for client in self._clients.values():
            peers[client.client_id] = client.methods

        await self._broadcast_ignore_result('_tell_peers', peers)
        await self._broadcast_ignore_result('on_start')

    def run(self):
        with _create_socket_dir() as socket_dir:
            socket_path = os.path.join(socket_dir, 'bel.socket')
            self._log.info('socket path: %s', socket_path)

            self._server_task = self._create_server_task(socket_path)
            self._socket_path = socket_path

            self._event_loop.create_task(self._send_start_event())

            try:
                self._event_loop.run_forever()
            except KeyboardInterrupt:
                pass

            # TODO
            self._event_loop.run_until_complete(self.shutdown())

            self._event_loop.stop()
            self._event_loop.run_forever()
            self._event_loop.close()
        self._socket_path = None
