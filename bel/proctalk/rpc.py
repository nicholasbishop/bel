from asyncio import CancelledError, Event, iscoroutine
from collections.abc import Mapping

from bel.proctalk.json_stream import JsonStream, JsonRpcFormatter
from bel.proctalk.future_group import FutureGroup
from bel.proctalk.typetrans import deserialize_and_call

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
        self._log.info('method call: %s %r', method_name, params)
        method = getattr(self._handler, method_name, None)
        if method is None:
            self._log.info('unhandled request: %s', method_name)
        elif getattr(method, 'expose', False) is not True:
            self._log.error('method is not exposed: %s', method_name)
        else:
            await self.call_method(mid, method, params)

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

    def _handle_error(self, msg):
        # TODO
        self._log.error('received error: %r', msg)

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
                self._handle_error(msg)
            else:
                self._log.error('invalid message: %r', msg)
        except CancelledError:
            self._log.info('rpc listen canceled')

    async def call_method(self, request_id, method, params):
        self._log.debug('calling method %s', method.__name__)

        result = deserialize_and_call(method, params)
        if iscoroutine(result):
            result = await result

        self._log.debug('method %s result: %r', method.__name__,
                        result)
        resp = self._formatter.response(result, request_id)
        await self._stream.write(resp)

    async def _call(self, method, list_params, dict_params):
        any_list_params = len(list_params) != 0
        any_dict_params = len(dict_params) != 0
        params = None
        if any_list_params and any_dict_params:
            raise RuntimeError('cannot call with both list and dict params',
                               method, list_params, dict_params)
        elif any_list_params:
            params = list_params
        elif any_dict_params:
            params = dict_params
        
        self._log.debug('send request: %s %r', method, params)

        req = self._formatter.request(method, params)
        mid = req['id']
        if mid in self._in_progress_requests:
            # TODO
            raise NotImplementedError(req)

        in_progress_request = InProgressRequest()
        self._in_progress_requests[mid] = in_progress_request
        await self._stream.write(req)
        return in_progress_request

    # TODO, API gets a bit complex, should simplify
    async def call_with_params(self, _method, params):
        if isinstance(params, Mapping):
            args = []
            kwargs = params
        else:
            args = params
            kwargs = {}
        
        await self._call(_method, args, kwargs)

    async def call_ignore_result(self, _method, *args, **kwargs):
        await self._call(_method, args, kwargs)

    async def call(self, _method, *args, **kwargs):
        in_progress_request = await self._call(_method, args, kwargs)
        return await in_progress_request.wait()
