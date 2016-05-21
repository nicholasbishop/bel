import capnp
import os
import subprocess
import sys
import time

class Launcher:
    def __init__(self, server_module_string, bootstrap_class_string,
                 bootstrap_capnp_type):
        interpreter = 'venv/bin/python3'
        # TODO
        self.socket_path = '/tmp/{}.socket'.format(bootstrap_class_string)
        self._capnp_socket_path = 'unix:' + self.socket_path
        self._bootstrap_capnp_type = bootstrap_capnp_type

        # Convenient place to insert vars or change command line
        self.env = dict(os.environ)
        self.env['PYTHONPATH'] = ':'.join(sys.path)
        self.cmd = []
        self.cmd += [interpreter, '-m', server_module_string,
                     self._capnp_socket_path, bootstrap_class_string]

        self.proc = None

    def launch(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
        self.proc = subprocess.Popen(self.cmd, env=self.env)
        # TODO
        for _ in range(2000):
            if os.path.exists(self.socket_path):
                break
            time.sleep(0.01)
        client = capnp.TwoPartyClient(self._capnp_socket_path)
        bootstrap = client.bootstrap().cast_as(self._bootstrap_capnp_type)
        print(bootstrap.sayHello().wait())

        return bootstrap
