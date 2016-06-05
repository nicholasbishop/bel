import json

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
        dct = {
            'jsonrpc': self._version,
            'method': method,
            'id': self._take_request_id()
        }
        if params is not None:
            dct['params'] = params
        return dct

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


class JsonEncoder(json.JSONEncoder):
    # pylint: disable=method-hidden
    def default(self, obj):
        serialize = getattr(obj, 'serialize', None)
        if serialize is None:
            return super().default(obj)
        else:
            return serialize()


class JsonStreamWriter:
    def __init__(self, stream):
        self._stream = stream

    async def write(self, data):
        string = json.dumps(data, cls=JsonEncoder)
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


class JsonStream:
    def __init__(self, in_stream, out_stream):
        self._in_stream = JsonStreamReader(in_stream)
        self._out_stream = JsonStreamWriter(out_stream)

    async def read(self):
        return await self._in_stream.read()

    async def write(self, data):
        await self._out_stream.write(data)
