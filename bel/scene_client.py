from bel.client import BaseClient, expose

class SceneClient(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @expose
    def set_background_color(self, color):
        # TODO
        self._log.info('set_background_color called: %r', color)
