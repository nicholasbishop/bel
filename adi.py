from asyncio import sleep

from bel.client import BaseClient
from bel.color import Color

class Adi(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = None

    async def on_start(self):
        self.scene = self._peers['bel.scene_client']

        #await self.scene.set_background_color(Color.random())
        await self.scene.set_background_color('hello')
    #     while self.running:
    #         await sleep(0.5)
