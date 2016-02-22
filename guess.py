#! /usr/bin/env python3

from bel import Scene

class Demo:
    def __init__(self):
        self.color1 = 1, 0, 0
        self.color2 = 0, 1, 0
        self.color3 = 0, 0, 1

        self.scene = Scene('hello world!')

        # Load an object and set its color
        self.obj = self.scene.load_path('path/to/my.obj')
        self.obj.color = self.color1

        # Add an event handler
        self.obj.on_click = self.handle_click

    def handle_click(self, event):
        """Cycle the object between three colors."""
        if self.obj.color == color1:
            self.obj.color = color2
        elif self.obj.color == color2:
            self.obj.color = color3
        else:
            self.obj.color = color1

    def run(self):
        self.scene.run()

Demo().run()
