from asyncio import create_subprocess_exec, get_event_loop, start_unix_server
from logging import getLogger
import os
import sys
from tempfile import TemporaryDirectory

from bel.ipc import JsonRpc

def _create_socket_dir():
    return TemporaryDirectory(prefix='bel-')


class Client:
    def __init__(self, client_id, proc_task):
        self._client_id = client_id
        self._proc_task = proc_task
        self._hub = None
        self._rpc = None

    async def get_proc(self):
        return await self._proc_task

    def connect(self, hub, rpc):
        self._hub = hub
        self._rpc = rpc
        self._rpc.set_handler(self)

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

    @property
    def event_loop(self):
        return self._event_loop

    async def _identify_client(self, rpc):
        def match_identity(identity):
            if identity in self._clients:
                self._clients[identity].connect(self, rpc)
            else:
                self._log.error('unknown client: %s', identity)
        await rpc.send_request(match_identity, '__identify')

    def _on_client_connect(self, reader, writer):
        self._log.info('client connected')
        rpc = JsonRpc('hub', reader, writer)
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
            proc = await client.get_proc()
            await proc.wait()
        self._event_loop.stop()

    async def _run_client(self):
        # TODO
        cmd = (sys.executable, '-m', 'bel.child', self._socket_path)
        proc = await create_subprocess_exec(*cmd)
        return proc

    def launch_client(self, client_id):
        self._log.info('launch client')
        if client_id in self._clients:
            raise KeyError('client key already exists', key)
        else:
            proc_task = self._event_loop.create_task(self._run_client())
            self._clients[client_id] = Client(client_id, proc_task)

    def run(self):
        with _create_socket_dir() as socket_dir:
            socket_path = os.path.join(socket_dir, 'bel.socket')
            self._log.info('socket path: %s', socket_path)

            self._server_task = self._create_server_task(socket_path)
            self._socket_path = socket_path
            try:
                self._event_loop.run_forever()
            except KeyboardInterrupt:
                pass

            # TODO
            #self.shutdown()

            self._event_loop.close()
        self._socket_path = None
