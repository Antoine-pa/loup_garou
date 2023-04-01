from .phases import Phases
import asyncio

class Data:
    def __init__(self):
        self.old_phase = ""

d = Data()

class Game(Phases):
    async def game(self, channel, client):
        await self.distribution(channel, client)
        while True:
            data = self.get_data(str(channel.id))
            if data["phase"] != d.old_phase:
                d.old_phase = data["phase"]
                await asyncio.sleep(1.5)
                if data["phase"] == "voleur":
                    await self.voleur(channel, client)
                elif data["phase"] == "enfant-sauvage":
                    await self.enfant_sauvage(channel, client)
                elif data["phase"] == "chien-loup":
                    await self.chien_loup(channel, client)
                elif data["phase"] == "cupidon":
                    await self.cupidon(channel, client)
                elif data["phase"] == "voyante":
                    await self.voyante(channel, client)
                elif data["phase"] == "loup":
                    await self.loups(channel, client)
                elif data["phase"] == "loup-blanc":
                    await self.loup_blanc(channel, client)
                elif data["phase"] == "sorciere":
                    await self.sorciere(channel, client)
                elif data["phase"] == "vote":
                    await self.vote(channel, client)
            await asyncio.sleep(0.5)