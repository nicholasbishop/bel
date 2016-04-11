from socket import AF_UNIX, SOCK_STREAM, socket
import sys

from bel import ipc
from bel.scene import Scene

def scene_server_main(server_sock):
    conn = ipc.Conn(server_sock)
    scene = Scene()
    # TODO
    while True:
        msg = conn.read_msg_nonblocking()
        if msg is not None:
            print(msg)


def main():
    socket_path = sys.argv[1]
    sock = socket(AF_UNIX, SOCK_STREAM)
    sock.connect(socket_path)
    scene_server_main(sock)


if __name__ == '__main__':
    main()


# Demo: launches scene and window processes
#
# Demo <-> scene
# scene <-> window
# 
