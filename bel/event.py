class Button:
    def __init__(self, button_id):
        self._bid = button_id

    def __eq__(self, other):
        return self._bid == other._bid

    def __hash__(self):
        return hash(self._bid)


class MouseDownEvent:
    def __init__(self, button, ):
        self._button = Button


class InputManager:
    def __init__(self, event_handler):
        self._event_handler = event_handler
        self._event_handler.set_input_manager(self)

        self._mouse_down_pos = {}
        self._mouse_pos = (0, 0)

    def mouse_down_pos(self, button):
        return self._mouse_down_pos[button]

    def feed(self, msg):
        if msg['tag'] == 'event_mouse_button':
            button = Button(msg['button'])
            if msg['action'] == 'press':
                if button in self._mouse_down_pos:
                    raise RuntimeError('sync error', msg)
                else:
                    self._event_handler.mouse_down(button)
                    self._mouse_down_pos[button] = self._mouse_pos
            elif msg['action'] == 'release':
                if button in self._mouse_down_pos:
                    self._event_handler.mouse_up(button)
                    del self._mouse_down_pos[button]
                else:
                    raise RuntimeError('sync error', msg)
            else:
                raise RuntimeError('unknown action', msg)
        elif msg['tag'] == 'event_mouse_move':
            pos = msg['pos']
            if len(self._mouse_down_pos) == 0:
                self._event_handler.mouse_move(pos)
            else:
                self._event_handler.mouse_drag(pos)
            self._mouse_pos = pos
