from asyncio import CancelledError, Event, iscoroutine
from collections.abc import Mapping

from bel.proctalk.json_stream import JsonStream, JsonRpcFormatter
from bel.proctalk.future_group import FutureGroup


def expose(method):
    method.expose = True
    return method


class InProgressRequest:
    def __init__(self):
        self._event = Event()
        self._result = None

    def response_received(self, result):
        self._result = result
        self._event.set()

    async def wait(self):
        await self._event.wait()
        return self._result


class JsonRpc:
    # TODO: remove name
    def __init__(self, name, reader, writer, event_loop, log):
        self._log = log
        self._stream = JsonStream(reader, writer)
        self._formatter = JsonRpcFormatter(name)
        self._in_progress_requests = {}
        self._running = True
        self._handler = None
        self._event_loop = event_loop
        self._future_group = FutureGroup(self._event_loop, self._log)

        self._create_listen_task()

    def _create_listen_task(self):
        if self._running:
            self._future_group.create_task(self._listen())

    def stop(self):
        self._running = False
        self._future_group.cancel_all()

    def set_handler(self, handler):
        self._handler = handler

    async def _handle_request(self, msg):
        for key in msg:
            if key not in ('id', 'jsonrpc', 'method', 'params'):
                raise KeyError('invalid key in request', key)
        method_name = msg['method']
        mid = msg['id']
        params = msg.get('params')
        self._log.info('method call: %s(%r)', method_name, params)
        method = getattr(self._handler, method_name, None)
        if method is None:
            self._log.info('unhandled request: %s', method_name)
        elif getattr(method, 'expose', False) is not True:
            self._log.error('method is not exposed: %s', method_name)
        else:
            await self.call_method(mid, method, params)

    async def _listen(self):
        msg = await self._stream.read()

        # Immediately create the new listen task, then proceed to
        # handle the current message. This allows the rest of the
        # message handling to block without also blocking new
        # messages.
        self._create_listen_task()

        try:
            if msg.get('jsonrpc') != '2.0':
                self._log.error('invalid message type: %r', msg)

            if 'method' in msg:
                await self._handle_request(msg)
            elif 'result' in msg:
                self._handle_response(msg)
            elif 'error' in msg:
                # TODO
                self._log.error('received error: %r', msg)
            else:
                # TODO
                self._log.error('invalid message: %r', msg)
        except CancelledError:
            self._log.info('rpc listen canceled')

    def _handle_response(self, msg):
        for key in msg:
            if key not in ('id', 'jsonrpc', 'result'):
                raise KeyError('invalid key in request', key)
        result = msg['result']
        mid = msg['id']
        in_progress_request = self._in_progress_requests.get(mid)
        if in_progress_request is None:
            self._log.error('response to unknown request: %r', msg)
        else:
            in_progress_request.response_received(result)

    async def call_method(self, request_id, method, params):
        self._log.debug('calling method %s', method.__name__)
        if params is None:
            result = method()
        elif isinstance(params, Mapping):
            result = method(**params)
        else:
            result = method(*params)
        if iscoroutine(result):
            result = await result
        self._log.debug('method %s result: %r', method.__name__,
                        result)
        resp = self._formatter.response(result, request_id)
        await self._stream.write(resp)

    async def _call(self, method, *args, **kwargs):
        self._log.debug('call: %s', method)

        any_args = len(args) != 0
        any_kwargs = len(kwargs) != 0
        params = None
        if any_args and any_kwargs:
            raise RuntimeError('cannot call with both args and kwargs',
                               method, args, kwargs)
        elif any_args:
            params = args
        elif any_kwargs:
            params = kwargs
        
        req = self._formatter.request(method, params)
        mid = req['id']
        if mid in self._in_progress_requests:
            # TODO
            raise NotImplementedError(req)

        in_progress_request = InProgressRequest()
        self._in_progress_requests[mid] = in_progress_request
        await self._stream.write(req)
        return in_progress_request

    async def call_ignore_result(self, method, *args, **kwargs):
        await self._call(method, *args, **kwargs)

    async def call(self, method, *args, **kwargs):
        in_progress_request = await self._call(method, *args, **kwargs)
        return await in_progress_request.wait()
