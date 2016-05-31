from bel.client import BaseClient, expose

class SceneClient(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._view = None

    @expose
    def on_start(self):
        self._view = self._peers['bel.glfw_client']

    @expose
    async def set_background_color(self, color):
        await self._view.set_clear_color(color)

    @expose
    def cursor_pos_event(self, xpos, ypos):
        pass
