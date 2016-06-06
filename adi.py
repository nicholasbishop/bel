from bel.proctalk.client import BaseClient
from bel.proctalk.rpc import expose

class Adi(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = None

    @expose
    async def on_start(self):
        self.scene = self._peers['bel.scene_client']

        await self.scene.load_obj('examples/xyz-text.obj')
