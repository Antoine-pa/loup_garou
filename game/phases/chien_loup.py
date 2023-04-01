from ..tools import *

class But(Button, Tools):
    def __init__(self, channel, client, name):
        self.channel = channel
        self.client = client
        self.name = name
        super().__init__(style=discord.ButtonStyle.blurple, label=self.name)
    
    async def callback(self, interaction: discord.Interaction):
        await self.edit_chienloup(interaction)
    
    async def edit_chienloup(self, interaction: discord.Interaction):
        data = self.get_data(self.channel.id)
        data = self.change_role(data, data["data_role"]["chien-loup"]["user_id"], self.name)
        data["data_role"]["chien-loup"]["role"] = self.name

        if self.name == "loup":
            channel_loup: discord.TextChannel = self.client.get_channel(data["channels"]["loup"])
            await channel_loup.set_permissions(self.client.get_user(data['data_role']['chien-loup']['user_id']), read_messages = True, send_messages = True, read_message_history=True)
            await channel_loup.send(f"{self.client.get_user(data['data_role']['chien-loup']['user_id']).mention} voici ton salon de vote lors de la nuit")
        
        await interaction.response.send_message(f"tu es désormais {self.name}")

        data["phase"] = "cupidon"
        self.push_data({str(self.channel.id) : data})
        self.view.clear_items()
        await interaction.response.edit_message(view = self.view)


class ViewBut(View, Tools):
    def __init__(self, client, channel, message):
        self.client = client
        self.channel = channel
        self.message = message
        super().__init__(timeout = 20)
        for name in "loup", "villageois":
            self.add_item(But(self.channel, self.client, name))
    
    async def on_timeout(self):
        data = self.get_data(self.channel.id)
        if data["data_role"]["chien-loup"]["role"] is None:
            await self.message.channel.send("tu n'as pas choisis ton camp, tu deviens donc villageois")
            self.clear_items()
            await self.message.edit(view = self)

            data = self.change_role(data, data["data_role"]["chien-loup"]["user_id"], "villageois")
            data["phase"] = "cupidon"
            self.push_data({str(self.channel.id) : data})



class ChienLoup(Tools):
    async def chien_loup(self, channel, client):
        data = self.get_data(channel.id)
        role = data["role_user"].get("chien-loup", None)
        if role is not None:
            message = await self.mp(client.get_user(role[0]), embed = discord.Embed(title = "Choix de votre role", description = "Tous les chiens savent au tréfonds d'eux-mêmes que leurs ancêtres étaient loups et que c'est l'Homme qui les a maintenus dans cet état de compagnons enfantins et craintifs, mais fidèles et généreux. En tout cas, seul le Chien-Loup peut décider s'il obéira à son maître humain et civilisé ou s'il écoutera l'appel de la nature sauvage enfouie dans ses entrailles."))
            await message.edit(view = ViewBut(client, channel, message))
        else:
            data["phase"] = "cupidon"
            self.push_data({str(self.channel.id) : data})