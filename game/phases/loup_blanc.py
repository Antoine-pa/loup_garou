from ..tools import *

class But(Button, Tools):
    def __init__(self, channel, client, user):
        self.channel = channel
        self.client = client
        self.user = user
        super().__init__(style = discord.ButtonStyle.blurple, label = str(self.user))
    
    async def callback(self, interaction: discord.Interaction):
        await self.edit_loupblanc(interaction)
    
    async def edit_loupblanc(self, interaction: discord.Interaction):
        data = self.get_data(self.channel.id)

        data["data_role"]["loup-blanc"]["kill"] = self.user.id
        await interaction.response.send_message(embed = discord.Embed(title = "Loup Blanc", description = f"vous venez de tuer {self.user}"))

        self.view.clear_items()
        await interaction.response.edit_message(view = self.view)

        data["phase"] = "sorciere"
        data["data_role"]["loup-blanc"]["activation"] = False
        self.push_data({str(self.channel.id) : data})


class ViewBut(View, Tools):
    def __init__(self, channel, client, message):
        self.channel = channel
        self.client = client
        self.message = message
        super().__init__(timeout = 20)
        data = self.get_data(self.channel.id)
        for user in data["liste_participant_en_vie"]:
            if user != data["data_role"]["loup-blanc"]["user_id"]:
                self.add_item(But(self.channel, self.client, user))
    
    async def on_timeout(self):
        data = self.get_data(self.channel.id)
        if data["data_role"]["loup_blanc"]["activation"]:
            self.clear_items()
            await self.message.edit(view = self)

            data["phase"] = "sorciere"
            data["data_role"]["loup-blanc"]["activation"] = False
            self.push_data({str(self.channel.id) : data})
    
class LoupBlanc(Tools):
    async def loup_blanc(self, channel, client):
        data = self.get_data(channel.id)
        loup_blanc = data["data_role"].get("loup-blanc", None)
        if loup_blanc is not None and loup_blanc["activation"]:
            message = await self.mp(client.get_user(loup_blanc["user_id"]), embed = discord.Embed(title = "Quel personne veux-tu tuer", description = "Tu dois choisir une personne a tuer (ton but est d'être le dernier survivant)")) #change
            await message.edit(view = ViewBut(channel, client, message))
        else:
            data["phase"] = "sorciere"
            data["data_role"]["loup-blanc"]["activation"] = True
            self.push_data({str(channel.id) : data})
        