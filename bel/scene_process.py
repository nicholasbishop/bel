from bel.child import main


class Scene:
    pass


def scene_main(conn):
    running = True
    while running:
        # TODO: timeout?
        msg = conn.read_msg_blocking()
        if msg['tag'] == 'exit':
            running = False


if __name__ == '__main__':
    main('sce', scene_main)
