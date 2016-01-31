#! /usr/bin/env python3

"""Process for all glfw/OpenGL operations."""

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


def main(pipe):
    """GPU process entry point."""
    width, height, title = pipe.recv()
    # width = 640
    # height = 480
    # title = 'asdf'
    try:
        print('b')
        init_glfw()
        print('c')
        print(width, height, title)
        window = glfw.CreateWindow(width, height, title)
        print('d')
        if not window:
            print('e')
            glfw.Terminate()
            pipe.send(('fatal', 'window'))
            print('f')

        glfw.MakeContextCurrent(window)
        print('g')
        while not glfw.WindowShouldClose(window):
            print('h')
            glfw.SwapBuffers(window)
            glfw.PollEvents()
            print('i')

        glfw.Terminate()
            
    except FatalInitializationError as err:
        pipe.send(('fatal', 'init'))
    print('x')


if __name__ == '__main__':
    main()
