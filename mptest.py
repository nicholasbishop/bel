#!/usr/bin/env python3

import multiprocessing
import threading

def friend():
    import cyglfw3 as glfw
    glfw.Init()
    window = glfw.CreateWindow(640, 480, 'pybliz')
    glfw.MakeContextCurrent(window)
    while not glfw.WindowShouldClose(window):
        glfw.SwapBuffers(window)
        glfw.PollEvents()
    print(threading.main_thread())


def main():
    print(threading.main_thread())
    proc = multiprocessing.Process(target=friend)
    proc.start()

main()
