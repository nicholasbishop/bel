#!/usr/bin/env python3

from multiprocessing import Pipe, Process
from pybliz import gpu_process

def main():
    parent_pipe, child_pipe = Pipe()
    proc = Process(target=gpu_process.main, args=(child_pipe,))
    proc.start()
    parent_pipe.send((640, 480, 'pybliz'))
    proc.join()

main()
