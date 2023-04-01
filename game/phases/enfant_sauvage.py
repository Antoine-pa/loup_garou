from ..tools import *

class But(Button, Tools):
    def __init__(self, channel, client, user):
        self.channel = channel
        self.client = client
        self.user = user
        super().__init__(style = discord.ButtonStyle.blurple, label = str(self.user))
    
    async def callback(self, interaction: discord.Interaction):
        await self.edit_enfant_sauvage(interaction)
    
    async def edit_enfant_sauvage(self, interaction: discord.Interaction):
        data = self.get_data(self.channel.id)

        data["data_role"]["enfant-sauvage"]["model"] = self.user.id
        await interaction.response.send_message(embed = discord.Embed(title = "Choix du référent", description = f"Votre référent devient {self.user}"))
        data = self.change_role(data, data["data_role"]["enfant-sauvage"]["user_id"], "villageois")

        self.view.clear_items()
        await interaction.response.edit_message(view = self.view)
        
        data["phase"] = "chien-loup"
        self.push_data({str(self.channel.id) : data})


class ViewBut(View, Tools):
    def __init__(self, channel, client, message):
        self.channel = channel
        self.client = client
        self.message = message
        super().__init__(timeout = 20)
        data = self.get_data(self.channel.id)

        for user in data['liste_participant_en_vie']:
            if user != data["data_role"]["enfant-sauvage"]["user_id"]:
                self.add_item(But(self.channel, self.client, self.client.get_user(user)))
    
    async def on_timeout(self):
        data = self.get_data(self.channel.id)
        if data["data_role"]["enfant-sauvage"]["model"] == None:

            model = __import__("random").choice(data["liste_participant_en_vie"].remove(data["data_role"]["enfant-sauvage"]["user_id"]))
            data["data_role"]["enfant-sauvage"]["model"] = model
            await self.message.channel.send(embed = discord.Embed(title = "Choix du référent", description = f"Votre référent devient {self.client.get_user(self.model)} (choix aléatoire vous n'avez pas répondu)"))
            data = self.change_role(data, data["data_role"]["enfant-sauvage"]["user_id"], "villageois")

            self.clear_items()
            await self.message.edit(view = self)

            data["phase"] = "chien-loup"
            self.push_data({str(self.channel.id) : data})


class EnfantSauvage(Tools):
    async def enfant_sauvage(self, channel, client):
        data = self.get_data(channel.id)
        role = data["role_user"].get("enfant-sauvage", None)
        if role is not None:
            message = await self.mp(client.get_user(role[0]), embed = discord.Embed(title = "Choix de votre model", description = "quel personne voulez vous suivre (si cette personne meurt vous devenez loup garou"))
            await message.edit(view = ViewBut(channel, client, message))
        else:
            data["phase"] = "chien-loup"
            self.push_data({str(channel.id) : data})