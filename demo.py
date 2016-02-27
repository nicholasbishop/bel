#! /usr/bin/env python3

from bel import Scene

class Demo:
    def __init__(self):
        self.color1 = 1, 0, 0
        self.color2 = 0, 1, 0
        self.color3 = 0, 0, 1

        # As soon as you create the Scene it starts running in a
        # separate process
        self.scene = Scene()

        # Load an object and set its color
        self.obj = self.scene.load_path('examples/cube.obj')
        self.obj.color = self.color1

        # Add an event handler
        self.obj.on_click = self.handle_click

    def handle_click(self, event):
        """Cycle the object between three colors."""
        if self.obj.color == self.color1:
            self.obj.color = self.color2
        elif self.obj.color == self.color2:
            self.obj.color = self.color3
        else:
            self.obj.color = self.color1

Demo()
