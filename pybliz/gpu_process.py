#! /usr/bin/env python3

"""Process for all glfw/OpenGL operations."""

import sys

import capnp
import pybliz_capnp
glfw = None


class FatalInitializationError(RuntimeError):
    pass


def init_glfw():
    # pylint: disable=locally-disabled,no-member
    import cyglfw3 as _glfw

    global glfw
    glfw = _glfw

    glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, 1)
    glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    if not glfw.Init():
        raise FatalInitializationError()


def main():
    """GPU process entry point."""
    address = sys.argv[1]
    client = capnp.TwoPartyClient(address)
    cap = client.ez_restore('gpu').cast_as(pylint_capnp.Gpu)

    # width, height, title = pipe.recv()
    width = 640
    height = 480
    title = 'asdf'
    try:
        init_glfw()
        print(width, height, title)
        window = glfw.CreateWindow(width, height, title)
        if not window:
            glfw.Terminate()
            pipe.send(('fatal', 'window'))

        glfw.MakeContextCurrent(window)
        while not glfw.WindowShouldClose(window):
            glfw.SwapBuffers(window)
            glfw.PollEvents()

        glfw.Terminate()
            
    except FatalInitializationError as err:
        pipe.send(('fatal', 'init'))


if __name__ == '__main__':
    main()
