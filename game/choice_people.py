from discord.ui import *
import discord
from .tools import *
from .choice_role import *

class But(View, ChoiceRole, Tools):
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel
        View.__init__(self, timeout = False)

    @button(label = "+ (add)", style = discord.ButtonStyle.blurple)
    async def _add(self, button: Button, interaction: discord.Interaction):
        message = interaction.message
        data = self.get_data(self.channel.id)
        if interaction.user.id in data["liste_participant"]:
            return
        dm = await interaction.user.create_dm()
        try:
            await dm.send("vous vous etes ajouté a la partie de loups garous")
        except discord.Forbidden:
            await self.channel.send("vos mp sont fermés", delete_after = 5)
            return
        data["liste_participant"].append(interaction.user.id)
        data = self.add_position(data, interaction.user)
        self.push_data({str(self.channel.id) : data})
        await self.make_description(client = self.client, channel = self.channel, message = message)
    
    @button(label = "- (sup)", style = discord.ButtonStyle.blurple)
    async def _sup(self, button: Button, interaction: discord.Interaction):
        message = interaction.message
        data = self.get_data(self.channel.id)
        if interaction.user.id not in data["liste_participant"]:
            return
        if data["createur"] == interaction.user.id:
            return
        data["liste_participant"].remove(interaction.user.id)
        data = self.del_position(data, interaction.user)
        self.push_data({str(self.channel.id) : data})
        await self.make_description(client = self.client, channel = self.channel, message = message)

    @button(label = "val", style = discord.ButtonStyle.green)
    async def _val(self, button: Button, interaction: discord.Interaction):
        data = self.get_data(self.channel.id)
        if data["createur"] != interaction.user.id:
            return
        """
        if len(data["liste_participant"]) < 6:
            return
        """
        data["liste_participant_en_vie"] = data["liste_participant"]
        self.push_data({str(self.channel.id) : data})
        await self.choice_role(client = self.client, channel = self.channel, message = interaction.message)
        return True

    @button(label = "del", style = discord.ButtonStyle.red)
    async def _del(self, button: Button, interaction: discord.Interaction):
        data = self.get_data(self.channel.id)
        if data["createur"] != interaction.user.id:
            return
        await interaction.message.delete()
        data = self.get_data()
        del data[str(self.channel.id)]
        self.push_data(data, overwrite = True)


class ChoicePeople(Tools):
    async def choice_people(self, client, ctx):
        await self.make_description(client = client, channel = ctx.channel, view = But(client, ctx.channel))