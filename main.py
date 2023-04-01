import discord
from discord.ext import commands
import json


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "!:", help_command = None, intents = intents)
client.load_extension("game.start")


@client.event
async def on_ready():
    with open("./data.json", "r") as file:
        data = json.load(file)
    for game in data.items():
        for channel in game[1]["channels"].items():
            if game[1]["delete_chan_after"]:
                channel: discord.TextChannel = client.get_channel(channel[1])
                await channel.delete()
    with open('./data.json', "w") as file:
        file.write(json.dumps({}, indent=4))
    print("start")

client.run("ODQ4NjAyMjkwMTE3ODA0MDcy.YLPAeA.3f6k88M1w7FWQpMkoUn7xK6DNsA")