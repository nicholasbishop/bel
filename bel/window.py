from logging import getLogger

from cyglfw3.compatible import (GLFW_CONTEXT_VERSION_MAJOR,
                                GLFW_CONTEXT_VERSION_MINOR,
                                GLFW_MOUSE_BUTTON_LEFT,
                                GLFW_MOUSE_BUTTON_MIDDLE,
                                GLFW_MOUSE_BUTTON_RIGHT,
                                GLFW_PRESS,
                                GLFW_RELEASE,
                                glfwCreateWindow,
                                glfwDestroyWindow,
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

from bel.buffer_object import ArrayBufferObject
from bel.color import Color
from bel.event import Button, ButtonAction, MouseButtonEvent
from bel.gldraw import DrawState
from bel.msg import BufferData
from bel.shader import ShaderProgram
from bel.transform import Transform
from bel.uniform import MatrixUniform
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
    def __init__(self):
        self._window = None
        self._draw_state = DrawState()
        self._init_glfw()
        self.on_draw = None
        self.on_start = None
        self.on_cursor_pos = None
        self.on_key = None

    def close(self):
        glfwSetWindowShouldClose(self._window, True)

    @property
    def draw_state(self):
        return self._draw_state

    @staticmethod
    def _cb_glfw_error(error, description):
        LOG.error('GLFW error: %d %s', error, description)

    def _cb_cursor_pos(self, window, xpos, ypos):
        if self.on_cursor_pos is not None:
            size = glfwGetWindowSize(window)
            loc = vec2(xpos / size[0], -ypos / size[1])
            self.on_cursor_pos(loc)

    def _cb_key(self, window, key, scancode, action, mods):
        if self.on_key is None:
            return
        self.on_key(key, scancode, action, mods)

    def _cb_mouse_button(self, window, gbutton, gaction, gmods):
        button = MouseButtonEvent(button_from_glfw(gbutton),
                                  button_action_from_glfw(gaction))
        #self._future_group.create_task(self._scene.mouse_button_event(button))

    def _init_glfw(self):
        if not glfwInit():
            raise RuntimeError('glfwInit failed')

        glfwSetErrorCallback(self._cb_glfw_error)

        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)

        # TODO
        self._window = glfwCreateWindow(800, 600, 'bel')
        if self._window is None:
            raise RuntimeError('glfwCreateWindow failed')

        glfwSetCursorPosCallback(self._window, self._cb_cursor_pos)
        glfwSetKeyCallback(self._window, self._cb_key)
        glfwSetMouseButtonCallback(self._window, self._cb_mouse_button)

        glfwMakeContextCurrent(self._window)
        LOG.info('GL_VERSION: %s', glGetString(GL_VERSION))

        self._add_default_materials()

    def _add_default_materials(self):
        # TODO
        default = ShaderProgram()
        default.update({
            'vert_shader_paths': ['shaders/vert.glsl'],
            'frag_shader_paths': ['shaders/frag.glsl'],
        })
        flat = ShaderProgram()
        flat.update({
            'vert_shader_paths': ['shaders/flat.vert.glsl'],
            'frag_shader_paths': ['shaders/flat.frag.glsl'],
        })
        self._draw_state.update_shader_program('default', default)
        self._draw_state.update_shader_program('flat', flat)

    def set_clear_color(self, color: Color):
        self._draw_state.clear_color = color

    def update_camera(self, transform: Transform):
        self._draw_state.update_uniform(
            'camera',
            MatrixUniform(transform.matrix())
        )

    def update_buffer(self, data: BufferData):
        glfwMakeContextCurrent(self._window)
        if data.uid not in self._draw_state.buffer_objects:
            self._draw_state.buffer_objects[data.uid] = ArrayBufferObject()
        self._draw_state.buffer_objects[data.uid].set_data(data.array)

    def update_draw_command(self, draw_command):
        self._draw_state.draw_commands[draw_command['uid']] = draw_command

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

    def stop(self):
        if self._window:
            glfwDestroyWindow(self._window)
            self._window = None

        # TODO, move to fgroup
        if self._poll_glfw_future is not None:
            self._poll_glfw_future.cancel()

        self._future_group.cancel_all()

        super().stop()
