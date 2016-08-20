from logging import getLogger

from cyglfw3.compatible import (GLFW_CONTEXT_VERSION_MAJOR,
                                GLFW_CONTEXT_VERSION_MINOR,
                                GLFW_MOUSE_BUTTON_LEFT,
                                GLFW_MOUSE_BUTTON_MIDDLE,
                                GLFW_MOUSE_BUTTON_RIGHT,
                                GLFW_PRESS,
                                GLFW_RELEASE,
                                glfwCreateWindow,
                                glfwGetFramebufferSize,
                                glfwGetWindowSize,
                                glfwInit,
                                glfwMakeContextCurrent,
                                glfwSetCursorPosCallback,
                                glfwSetErrorCallback,
                                glfwSetKeyCallback,
                                glfwSetMouseButtonCallback,
                                glfwSetWindowShouldClose,
                                glfwSwapBuffers,
                                glfwWaitEvents,
                                glfwWindowHint,
                                glfwWindowShouldClose)
from OpenGL.GL import GL_VERSION, glGetString

from bel.default_material import default_material
from bel.color import Color
from bel.event import Button, ButtonAction, MouseButtonEvent
from bel.gldraw import DrawState
from bel.shader import (FragmentShader, GeometryShader, ShaderProgram,
                        VertexShader)
from cgmath.vector import vec2

LOG = getLogger(__name__)

def button_from_glfw(glfw_button):
    if glfw_button == GLFW_MOUSE_BUTTON_LEFT:
        return Button.Left
    elif glfw_button == GLFW_MOUSE_BUTTON_MIDDLE:
        return Button.Middle
    elif glfw_button == GLFW_MOUSE_BUTTON_RIGHT:
        return Button.Right
    else:
        raise NotImplementedError('unknown button type', glfw_button)


def button_action_from_glfw(glfw_button_action):
    if glfw_button_action == GLFW_PRESS:
        return ButtonAction.Press
    elif glfw_button_action == GLFW_RELEASE:
        return ButtonAction.Release
    else:
        raise ValueError('invalid action', glfw_button_action)


class Window:
    def __init__(self, width=800, height=600):
        self._window = None
        self.on_draw = lambda *args: None
        self.on_start = lambda *args: None
        self.on_cursor_pos = lambda *args: None
        self.on_key = lambda *args: None
        self.on_mouse_button = lambda *args: None
        self._draw_state = DrawState()
        self._init_glfw(width, height)

    def close(self):
        glfwSetWindowShouldClose(self._window, True)

    @property
    def draw_state(self):
        return self._draw_state

    @staticmethod
    def _cb_glfw_error(error, description):
        LOG.error('GLFW error: %d %s', error, description)

    def _cb_cursor_pos(self, window, xpos, ypos):
        # normalize cursor position: [-1, 1] in x and y
        width, height = glfwGetWindowSize(window)
        loc = vec2((2.0 * xpos) / width - 1.0,
                   1.0 - (2.0 * ypos) / height)
        self.on_cursor_pos(loc)

    def _cb_key(self, window, key, scancode, action, mods):
        self.on_key(key, scancode, action, mods)

    def _cb_mouse_button(self, window, button, action, mods):
        event = MouseButtonEvent(button_from_glfw(button),
                                 button_action_from_glfw(action))

        self.on_mouse_button(event)

    def _init_glfw(self, width, height):
        if not glfwInit():
            raise RuntimeError('glfwInit failed')

        glfwSetErrorCallback(self._cb_glfw_error)

        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)

        # TODO
        self._window = glfwCreateWindow(width, height, 'bel')
        if self._window is None:
            raise RuntimeError('glfwCreateWindow failed')

        glfwSetCursorPosCallback(self._window, self._cb_cursor_pos)
        glfwSetKeyCallback(self._window, self._cb_key)
        glfwSetMouseButtonCallback(self._window, self._cb_mouse_button)

        glfwMakeContextCurrent(self._window)
        LOG.info('GL_VERSION: %s', glGetString(GL_VERSION).decode())

        # TODO
        self._draw_state.fb_size = glfwGetFramebufferSize(self._window)

        self._add_default_materials()

    def _add_default_materials(self):
        # TODO
        default = ShaderProgram.from_material(default_material())

        flat = ShaderProgram()
        flat.update(
            VertexShader('shaders/flat.vert.glsl'),
            FragmentShader('shaders/flat.frag.glsl'))
        self._draw_state.update_shader_program('default', default)
        self._draw_state.update_shader_program('flat', flat)

    def set_clear_color(self, color: Color):
        self._draw_state.clear_color = color

    def _draw(self):
        self._draw_state.fb_size = glfwGetFramebufferSize(self._window)
        self.on_draw()

        self._draw_state.draw_all()

    def run(self):
        running = True
        while running:
            glfwMakeContextCurrent(self._window)
            self._draw()
            glfwSwapBuffers(self._window)
            glfwWaitEvents()

            if glfwWindowShouldClose(self._window):
                running = False
