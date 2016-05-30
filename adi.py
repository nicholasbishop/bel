from asyncio import sleep

from bel.client import BaseClient
from bel.color import Color

class Adi(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self._scene = self._create_dispatcher('bel.scene_client')

    # async def on_start(self):
    #     while self.running:
    #         #await self._scene.set_background_color(Color.random())
    #         await sleep(0.5)
