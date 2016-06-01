class DrawState:
    def __init__(self):
        self.clear_color = Color(0.4, 0.4, 0.5, 1.0)
        self.buffer_objects = {}
        self.draw_commands = {}
