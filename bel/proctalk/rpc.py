from asyncio import get_event_loop, iscoroutinefunction
import logging


from bel.proctalk.json_stream import JsonStream, JsonRpcFormatter


def exactly_one_of(*items):
    found = False
    for item in items:
        if item is True:
            if found is True:
                return False
            else:
                found = True
    return found


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

    async def _listen(self):
        msg = await self._stream.read()
        if msg['jsonrpc'] != '2.0':
            # TODO
            raise NotImplementedError(msg)
        method_name = msg.get('method')
        result = msg.get('result')
        error = msg.get('error')

        if not exactly_one_of('method' in msg,
                              'result' in msg,
                              'error' in msg):
            # TODO
            raise NotImplementedError(msg)

        mid = msg.get('id')
        if method_name is not None:
            params = msg.get('params', [])
            logging.info('method call: %s(%r)', method_name, params)

            method = getattr(self._handler, method_name, None)
            if method is None:
                # TODO
                print('unhandled request', msg)
            else:
                get_event_loop().create_task(self.call_method(mid, method,
                                                              params))
        elif result is not None:
            self._handle_response(result, mid)
        elif error is not None:
            # TODO
            print('received error', msg)

        # TODO, exception handling

        if self._running:
            self._create_listen_task()

    def _handle_response(self, result, mid):
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
