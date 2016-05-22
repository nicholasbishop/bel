from enum import Enum, unique

import dill


@unique
class Tag(Enum):
    Exit = 1
    SCE_SetBackgroundColor = 2
    WND_SetClearColor = 3
    SCE_EventMouseButton = 4
    SCE_EventWindowSize = 5
    SCE_EventCursorPosition = 6
    SCE_AttachEventHandler = 7
    SCE_LoadObject = 8,
    WND_UpdateBuffer = 9,
    WND_UpdateDrawCommand = 10,
    WND_UpdateMaterial = 11,


class Msg:
    def __init__(self, tag, body=None):
        self._tag = tag
        self._body = body

    @property
    def tag(self):
        return self._tag

    @property
    def body(self):
        return self._body

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
