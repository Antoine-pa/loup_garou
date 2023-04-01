from discord.ext import commands
from discord.ui import *
from .choice_people import *
from .tools import *


class Start(commands.Cog, ChoicePeople, Tools):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def start(self, ctx):
        data = {str(ctx.channel.id) : {
            "createur" : ctx.author.id,
            "delete_chan_after": True,
            "liste_participant" : [ctx.author.id],
            "liste_participant_en_vie" : [],
            "positions": [
                [
                    ctx.author.id, {
                        "droite": ctx.author.id,
                        "gauche": ctx.author.id
                    }
                ]
            ],
            "liste_role" : [],
            "channels": {},
            "user_role" : {},
            "role_user" : {},
            "data_role" : {
                "voleur" : [],
                "loup" : {
                    "vote" : {},
                    "kill" : None
                },
                "cupidon" : [],
                "voyante" : {},
                "sorciere" : {
                    "sauver" : 1,
                    "tuer" : 1,
                    "kill" : None
                },
                "chien-loup": {
                    "user_id": None,
                    "role": None
                },
                "enfant-sauvage": {
                    "user_id": None,
                    "model": None
                },
                "loup-blanc" : {
                    "user_id": None,
                    "activation" : True,
                    "kill": None
                },
                "vote": {}
            },
            "phase" : "voleur"
        }}
        self.push_data(data)
        await self.choice_people(client = self.client, ctx = ctx)
    

def setup(client):
    client.add_cog(Start(client))