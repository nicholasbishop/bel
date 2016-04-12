from importlib import import_module
import sys

import capnp


def create_bootstrap_object(bootstrap_string):
    module_name, class_name = bootstrap_string.rsplit('.', 1)
    module = import_module(module_name)
    bootstrap_class = getattr(module, class_name)
    return bootstrap_class()


def run_server():
    socket_path = sys.argv[1]
    bootstrap_string = sys.argv[2]
    print('socket_path:', socket_path, ' bootstrap:', bootstrap_string)

    bootstrap_object = create_bootstrap_object(bootstrap_string)

    server = capnp.TwoPartyServer(socket_path, bootstrap=bootstrap_object)
    server.run_forever()


if __name__ == '__main__':
    run_server()
