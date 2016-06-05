from bel.camera import Camera
from bel.client import BaseClient, expose
from bel.event import MouseButtonEvent
from bel.mesh import Mesh
from bel.proctalk.future_group import FutureGroup

class SceneClient(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._view = None
        self._mesh = None
        self._camera = Camera()
        self._future_group = FutureGroup(self._event_loop, self._log)

    def _create_flush_task(self):
        self._future_group.create_task(self._flush())

    def _flush(self):
        # TODO
        pass

    @expose
    def shutdown(self):
        self._future_group.cancel_all()
        super().shutdown()

    @expose
    async def on_start(self):
        self._view = self._peers['bel.glfw_client']
        await self._camera.flush_updates(self._view)

    @expose
    async def load_obj(self, path):
        self._mesh = Mesh.load_obj(path)
        await self._mesh.flush_updates(self._view)

    @expose
    async def set_background_color(self, color):
        await self._view.set_clear_color(color)

    @expose
    def cursor_pos_event(self, xpos, ypos):
        pass

    @expose
    def mouse_button_event(self, event: MouseButtonEvent):
        pass
