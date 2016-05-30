from asyncio import Event, get_event_loop, iscoroutinefunction
import logging

from bel.proctalk.json_stream import JsonStream, JsonRpcFormatter


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
    def __init__(self, name, reader, writer, event_loop=None):
        self._stream = JsonStream(reader, writer)
        self._formatter = JsonRpcFormatter(name)
        self._in_progress_requests = {}
        self._running = True
        self._handler = None
        self._event_loop = event_loop or get_event_loop()
        self._create_listen_task()

    def _create_listen_task(self):
        self._listen_task = self._event_loop.create_task(self._listen())
        def handle_exception(task):
            if task.cancelled():
                return
            exc = task.exception()
            if exc is not None:
                # TODO, handle in some way
                logging.error('listen exception: %s', exc)
        self._listen_task.add_done_callback(handle_exception)

    def stop(self):
        self._running = False
        self._listen_task.cancel()

    def set_handler(self, handler):
        self._handler = handler

    async def _handle_request(self, msg):
        for key in msg:
            if key not in ('id', 'jsonrpc', 'method', 'params'):
                raise KeyError('invalid key in request', key)
        method_name = msg['method']
        mid = msg['id']
        params = msg['params']
        logging.info('method call: %s(%r)', method_name, params)
        method = getattr(self._handler, method_name, None)
        if method is None:
            # TODO
            print('unhandled request', msg)
        else:
            get_event_loop().create_task(self.call_method(mid, method,
                                                          params))

    async def _listen(self):
        msg = await self._stream.read()

        try:
            if msg.get('jsonrpc') != '2.0':
                logging.error('invalid message type', msg)

            if 'method' in msg:
                await self._handle_request(msg)
            elif 'result' in msg:
                self._handle_response(msg)
            elif 'error' in msg:
                # TODO
                print('received error', msg)
            else:
                # TODO
                logging.error('invalid message', msg)
        except Exception:
            logging.exception('unhandled exception')
            raise
        finally:
            if self._running:
                self._create_listen_task()

    def _handle_response(self, msg):
        for key in msg:
            if key not in ('id', 'jsonrpc', 'result'):
                raise KeyError('invalid key in request', key)
        result = msg['result']
        mid = msg['id']
        in_progress_request = self._in_progress_requests.get(mid)
        if in_progress_request is None:
            logging.error('response to unknown request', msg)
        else:
            in_progress_request.response_received(result)

    async def call_method(self, request_id, method, params):
        logging.debug('calling method %s', method.__name__)
        if iscoroutinefunction(method):
            result = await method(*params)
        else:
            result = method(*params)
        logging.debug('method %s result: %r', method.__name__,
                      result)
        resp = self._formatter.response(result, request_id)
        return await self._stream.write(resp)

    async def call_ignore_result(self, method, *args):
        logging.info('call_ignore_result: %s(%r)', method, args)
        req = self._formatter.request(method, args)
        await self._stream.write(req)

    async def call(self, method, *args):
        logging.info('call: %s(%r)', method, args)
        req = self._formatter.request(method, args)
        mid = req['id']
        if mid in self._in_progress_requests:
            # TODO
            raise NotImplementedError(req)

        in_progress_request = InProgressRequest()
        self._in_progress_requests[mid] = in_progress_request
        await self._stream.write(req)
        return await in_progress_request.wait()
