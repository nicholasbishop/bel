from asyncio import sleep

from bel.client import BaseClient
from bel.color import Color

class Adi(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_start(self):
        #await self.scene.set_background_color(Color.random())
        await self.scene.set_background_color('hello')
    #     while self.running:
    #         await sleep(0.5)
