from enum import Enum, unique

import dill


@unique
class Tag(Enum):
    Exit = 1
    SetBackgroundColor = 2
    SetClearColor = 3


class Msg:
    def __init__(self, tag, body=None):
        self._tag = tag
        self._body = body

    @property
    def tag(self):
        return self._tag

    @classmethod
    def decode(cls, raw_msg):
        msg = dill.loads(raw_msg)
        return Msg(Tag(msg[0]), msg[1])

    def encode(self):
        return dill.dumps([
            self._tag,
            self._body
        ])


class UpdateBufferObject:
    def __init__(self, name, contents):
        self.name = name
        self.contents = contents
