from bel.child import main
from bel.msg import Tag


class Scene:
    pass


def scene_main(conn):
    running = True
    while running:
        # TODO: timeout?
        msg = conn.read_msg_blocking()
        if msg.tag == Tag.Exit:
            running = False


if __name__ == '__main__':
    main('sce', scene_main)
