from enum import Enum, unique

@unique
class ButtonAction(Enum):
    Press = 0,
    Release = 1

@unique
class Button(Enum):
    Left = 0,
    Middle = 1,
    Right = 2

# TODO(nicholasbishop): add mods to match glfw
class MouseButtonEvent:
    def __init__(self, button, action):
        self._button = button
        self._action = action

    @property
    def button(self):
        return self._button

    @property
    def action(self):
        return self._action

    def serialize(self):
        return (self._button, self._action)

    def deserialize(self, seq):
        return MouseButtonEvent(*seq)
