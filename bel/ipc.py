from asyncio import get_event_loop
import json
import logging

class JsonRpcFormatter:
    def __init__(self, name):
        self._name = name
        self._next_request_id = 1

    def _take_request_id(self):
        request_id = '{}-{}'.format(self._name, self._next_request_id)
        self._next_request_id += 1
        return request_id

    def request(self, method, params):
        return {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': self._take_request_id()
        }

    def response(self, result, request_id):
        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': request_id
        }

    def error(self, code, message, request_id):
        return {
            'jsonrpc': '2.0',
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

        if event_loop is None:
            event_loop = get_event_loop()
        event_loop.create_task(self._listen_forever())

    def stop(self):
        self._running = False

    def set_handler(self, handler):
        self._handler = handler

    async def _listen_forever(self):
        while self._running:
            await self._listen_one()

    async def _listen_one(self):
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

    def _handle_response(self, result, mid):
        callback = self._callbacks[mid]
        callback(result)

    async def call_method(self, request_id, method, params):
        result = await method(*params)
        resp = self._formatter.response(result, request_id)
        return await self._writer.write(resp)
        
    async def send_request(self, callback, method, params):
        logging.info('send_request: %s(%r)', method, params)
        req = self._formatter.request(method, params)
        if callback is not None:
            rid = req['id']
            if rid in self._callbacks:
                # TODO
                raise NotImplementedError(req)
            self._callbacks[rid] = callback
        return await self._writer.write(req)
