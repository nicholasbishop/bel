from asyncio import get_event_loop
import json
import logging

class JsonRpcFormatter:
    def __init__(self, name, version='2.0'):
        self._name = name
        self._next_request_id = 1
        self._version = version

    @property
    def name(self):
        return self._name

    def _take_request_id(self):
        request_id = '{}-{}'.format(self._name, self._next_request_id)
        self._next_request_id += 1
        return request_id

    def request(self, method, params):
        return {
            'jsonrpc': self._version,
            'method': method,
            'params': params,
            'id': self._take_request_id()
        }

    def response(self, result, request_id):
        return {
            'jsonrpc': self._version,
            'result': result,
            'id': request_id
        }

    def error(self, code, message, request_id):
        return {
            'jsonrpc': self._version,
            'error': {
                'code': code,
                'message': message
            },
            'id': request_id
        }


SIZE_FIELD_IN_BYTES = 8


class JsonStreamWriter:
    def __init__(self, stream):
        self._stream = stream

    async def write(self, data):
        string = json.dumps(data)
        encoded = string.encode()
        pad = '{:0' + str(SIZE_FIELD_IN_BYTES) + '}'
        size_field = pad.format(len(encoded)).encode()
        self._stream.write(size_field)
        self._stream.write(encoded)
        await self._stream.drain()


class JsonStreamReader:
    def __init__(self, stream):
        self._stream = stream

    async def read(self):
        size_field = await self._stream.readexactly(SIZE_FIELD_IN_BYTES)
        size = int(size_field)
        raw_msg = await self._stream.readexactly(size)
        string_msg = raw_msg.decode()
        return json.loads(string_msg)


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
        self._reader = JsonStreamReader(reader)
        self._writer = JsonStreamWriter(writer)
        self._formatter = JsonRpcFormatter(name)
        self._callbacks = {}
        self._running = True
        self._handler = None
        self._event_loop = event_loop or get_event_loop()
        self._create_listen_task()

    def _create_listen_task(self):
        self._listen_task = self._event_loop.create_task(self._listen())
        def handle_exception(task):
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
        msg = await self._reader.read()
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

            if method_name == '__identify':
                get_event_loop().create_task(self._report_identity(mid))
            else:
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
        result = await method(*params)
        resp = self._formatter.response(result, request_id)
        return await self._writer.write(resp)

    async def _report_identity(self, request_id):
        identity = self._formatter.name
        logging.debug('reporting identity as "%s"', identity)
        resp = self._formatter.response(identity, request_id)
        return await self._writer.write(resp)

    async def send_request(self, callback, method, *args):
        logging.info('send_request: %s(%r)', method, args)
        req = self._formatter.request(method, args)
        if callback is not None:
            rid = req['id']
            if rid in self._callbacks:
                # TODO
                raise NotImplementedError(req)
            self._callbacks[rid] = callback
        return await self._writer.write(req)
