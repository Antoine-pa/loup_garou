from discord.ui import *
import discord
from .tools import *
from .game import *

class But(Button, Game, Tools):
    def __init__(self, client, channel, name, color, disabled):
        self.client = client
        self.channel = channel
        self.name = name
        self.color = color
        self.auto_role = ["loup-blanc", "villageois", "loup", "villageois", "voyante", "sorciere", "villageois", "cupidon", "loup", "chasseur", "voleur", "villageois", "garde", "loup"]
        super().__init__(style = self.color, label = self.name, disabled = disabled)
    
    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        data = self.get_data(self.channel.id)
        view: ViewBut = self.view

        if self.name == "auto":
            data["liste_role"] = self.auto_role[:len(data["liste_participant"])]
            if "voleur" in data["liste_role"]:
                for _ in range(2):
                    data["liste_role"].append("villageois")
            for but in view.children:
                if but.label == "val":
                    but.disabled = False
            await message.edit(view = view)

        elif self.name == "preserve_chan":
            data["delete_chan_after"] = False
            self.push_data({str(self.channel.id) : data})
            self.disabled = True
            await message.edit(view = view)
            self.push_data({str(self.channel.id) : data})
            return True
            
        elif self.name == "val":
            await interaction.response.edit_message(view = View(0))
            for role in data["liste_role"]:
                overwrites = {
                        self.channel.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                        self.channel.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_roles=True, manage_permissions=True, manage_messages=True, read_message_history=True)
                    }
                if (role in ("loup", "loup-blanc")) and data["channels"].get("loup", None) is None:
                    channel_loup = await self.channel.guild.create_text_channel(name = 'LOUPS', overwrites=overwrites, category = self.channel.category)
                    data["channels"]["loup"] = channel_loup.id
                
                elif role == "cupidon" and data["channels"].get("cupidon", None) is None:
                    channel_amoureux = await self.channel.guild.create_text_channel(name = 'AMOUREUX', overwrites=overwrites, category = self.channel.category)
                    data["channels"]["amoureux"] = channel_amoureux.id  

            self.push_data({str(self.channel.id) : data})
            await self.game(channel = self.channel, client = self.client)

        elif self.name == "del":
            if data["createur"] != interaction.user.id:
                return
            await interaction.message.delete()
            data = self.get_data()
            del data[str(self.channel.id)]
            self.push_data(data, overwrite = True)
            return True

        self.push_data({str(self.channel.id) : data})
        await self.make_description(client = self.client, channel = self.channel, message = message)
        return True

class ViewBut(View, Tools):
    def __init__(self, client, channel):
        super().__init__(timeout=False)
        self.client = client
        self.channel = channel
        for but in (("auto", discord.ButtonStyle.blurple, False), ("preserve_chan", discord.ButtonStyle.blurple, False), ("val", discord.ButtonStyle.green, True), ("del", discord.ButtonStyle.red, False)):
            self.add_item(But(self.client, self.channel, but[0], but[1], but[2]))

class ChoiceRole(Tools):
    async def choice_role(self, client, channel, message):
        await self.make_description(client = self.client, channel = channel, message = message, view = ViewBut(client = client, channel = channel))