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
                                glfwInit,
                                glfwMakeContextCurrent,
                                glfwPollEvents,
                                glfwSetCursorPosCallback,
                                glfwSetErrorCallback,
                                glfwSetMouseButtonCallback,
                                glfwSwapBuffers,
                                glfwWindowHint,
                                glfwWindowShouldClose)
from OpenGL.GL import GL_VERSION, glGetString

from bel.buffer_object import ArrayBufferObject
from bel.client import BaseClient, expose
from bel.color import Color
from bel.event import Button, ButtonAction, MouseButtonEvent
from bel.proctalk.future_group import FutureGroup
from bel.gldraw import DrawState
from bel.msg import BufferData
from bel.shader import ShaderProgram
from bel.transform import Transform
from bel.uniform import MatrixUniform

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


class GlfwClient(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._poll_glfw_future = None
        self._window = None
        self._draw_state = DrawState()
        self._scene = None
        self._future_group = FutureGroup(self._event_loop, self._log)

        self._init_glfw()

    @expose
    def on_start(self):
        self._scene = self._peers['bel.scene_client']

    def _cb_glfw_error(self, error, description):
        self._log.error('GLFW error: %d %s', error, description)

    def _cb_cursor_pos(self, window, xpos, ypos):
        self._future_group.create_task(self._scene.cursor_pos_event(xpos, ypos))

    def _cb_mouse_button(self, window, gbutton, gaction, gmods):
        button = MouseButtonEvent(button_from_glfw(gbutton),
                                  button_action_from_glfw(gaction))
        self._future_group.create_task(self._scene.mouse_button_event(button))

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
        glfwSetMouseButtonCallback(self._window, self._cb_mouse_button)

        glfwMakeContextCurrent(self._window)
        self._log.info('GL_VERSION: %s', glGetString(GL_VERSION))

        self._add_default_materials()

        self._poll_glfw_events()

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

    @expose
    def set_clear_color(self, color: Color):
        self._draw_state.clear_color = color

    @expose
    def update_camera(self, transform: Transform):
        self._draw_state.update_uniform(
            'camera',
            MatrixUniform(transform.matrix())
        )

    @expose
    def update_buffer(self, data: BufferData):
        glfwMakeContextCurrent(self._window)
        if data.uid not in self._draw_state.buffer_objects:
            self._draw_state.buffer_objects[data.uid] = ArrayBufferObject()
        self._draw_state.buffer_objects[data.uid].set_data(data.array)

    @expose
    def update_draw_command(self, draw_command):
        self._draw_state.draw_commands[draw_command['uid']] = draw_command

    def _draw(self):
        self._draw_state.fb_size = glfwGetFramebufferSize(self._window)

        self._draw_state.draw_all()

    def _poll_glfw_events(self):
        glfwMakeContextCurrent(self._window)
        self._draw()
        glfwSwapBuffers(self._window)
        glfwPollEvents()

        if glfwWindowShouldClose(self._window):
            self.running = False
            self.shutdown()

        if self.running:
            # TODO
            delay = 1 / 120
            future = self._event_loop.call_later(delay, self._poll_glfw_events)
            self._poll_glfw_future = future

    def stop(self):
        if self._window:
            glfwDestroyWindow(self._window)
            self._window = None

        # TODO, move to fgroup
        if self._poll_glfw_future is not None:
            self._poll_glfw_future.cancel()

        self._future_group.cancel_all()

        super().stop()
