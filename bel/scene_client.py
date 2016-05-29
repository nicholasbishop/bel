from bel.client import BaseClient

class SceneClient(BaseClient):
    def __init__(self, log, event_loop, rpc):
        super().__init__(log, event_loop, rpc)
