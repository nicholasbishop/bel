from asyncio import get_event_loop, iscoroutinefunction
import logging

from bel.proctalk.json_stream import JsonStream, JsonRpcFormatter


class JsonRpc:
    def __init__(self, name, reader, writer, event_loop=None):
        self._stream = JsonStream(reader, writer)
        self._formatter = JsonRpcFormatter(name)
        self._callbacks = {}
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
        callback = self._callbacks[mid]
        callback(result)

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

    async def send_request(self, callback, method, *args):
        logging.info('send_request: %s(%r)', method, args)
        req = self._formatter.request(method, args)
        if callback is not None:
            rid = req['id']
            if rid in self._callbacks:
                # TODO
                raise NotImplementedError(req)
            self._callbacks[rid] = callback
        return await self._stream.write(req)
