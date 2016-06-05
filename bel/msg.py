import numpy

from base64 import b64encode, b64decode


class BufferData:
    def __init__(self, uid, array):
        self._uid = uid
        self._array = array

    @property
    def uid(self):
        return self._uid

    @property
    def array(self):
        return self._array

    def serialize(self):
        return dict(
            uid=self._uid,
            array=b64encode(self._array).decode('ascii'),
        )

    @classmethod
    def deserialize(self, dct):
        array = b64decode(dct['array'].encode('ascii'))
        return BufferData(
            uid=dct['uid'],
            array=numpy.frombuffer(array, dtype=numpy.float32)
        )
